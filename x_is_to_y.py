from nltk.corpus import wordnet as wn
import random
from typing import Dict, List
import json
from itertools import chain
from nltk.stem import *
from nltk.stem.porter import *
from fuzzywuzzy import fuzz

class XIsToYMaker:
    def __init__(self, length_limit: int = 8):
        self.wn = wn
        self.words_in_wn = list(set(i for i in wn.words()))
        self.wn_length = len(self.words_in_wn)
        self.length_limit = length_limit
        self.stemmer = PorterStemmer()

    def _get_fuzz_score(self, word1: str, word2: str) -> int:
        return fuzz.partial_ratio(word1, word2)
    
    # note, random words will lean towards very obscure words, some form of filtering or starting word set that is narrowed and more common
    def get_random_word(self) -> str:
        random_index = random.randrange(0, self.wn_length)
        random_word = self.words_in_wn[random_index]
        return random_word
    
    def _get_and_save_simple_words(self, num_words: int = 5000000):
        # method to get lots of words and save the ones that are below certain length or simplicity (look into methods for readability of single word?)
        word_list = []
        for word in range(num_words):
            random_word = self.get_random_word()
            if len(random_word) <= self.length_limit and "_" not in random_word and random_word.isalpha():
                word_list.append(random_word)
        data_to_write = {f"words_under_{self.length_limit}" : word_list}
        with open('word_info.json', 'w') as f:
            json.dump(data_to_write, f)
        print(len(word_list))
        # TODO: read in existing data and append to same num of words or add new key
        return word_list

    def get_synsets(self, word: str):
        synset = wn.synsets(word)
        num_synsets = len(synset)
        return synset, num_synsets # note will have variable number of synsets for different words

    def get_word_from_synset(self, synset):
        # TODO: could do some shuffling of lemmas?
        word = str(synset.lemmas()[0].name())
        return word
    
    def get_lemma_from_synset(self, synset):
        lemma = synset.lemmas()[0]
        return lemma

    # TODO: get synonyms, antonyms, hyponym, meronym (larger or smaller of given category), troponym (way of doing the thing), entailment (x entails y, prerequisite/one implies another)
    def get_synonyms(self, synset):
        word = self.get_word_from_synset(synset)
        synonyms = wn.synonyms(word)
        return synonyms

    def get_random_word_from_file(self) -> str:
        # TODO: get based on max len key if available
        word_file = open("word_info.json")
        word_info = json.load(word_file)
        word_list = word_info.get(f"words_under_{self.length_limit}")
        random_word = random.choice(word_list)
        return random_word
        # TODO: else create some?

    def _validate_related_words(self, word1: str, related: List[List[str]]) -> List[any]:
        if len(related) > 0 and type(related[0]) == list:
            related_chained = list(chain.from_iterable(related))
        else:
            related_chained = related
        print(related_chained)
        valid_words = []
        for word in related_chained:
            # exclude words with same stem e.g. don't want look and looked as synonyms
            if self.stemmer.stem(word) != self.stemmer.stem(word1) and self._get_fuzz_score(word, word1) <= 95:
                if not "_" in word and len(word) > 0 and word.isalpha() == True:
                    # TODO: more validation e.g. remove scientific e.g. starts with genus_ but mostly covered by underscore exclusion?
                    valid_words.append(word)
        if len(valid_words) > 0:
            random_valid_word = random.choice(valid_words)
            return [True, random_valid_word]
        else: return [False, ""]

    def create_synonym_question(self) -> Dict:
        # create first pair with target relation based on random word
        start_word = self.get_random_word_from_file()
        
        synsets, num_synsets = self.get_synsets(start_word)
        
        all_synonyms_start_word = list(chain.from_iterable([ self.get_synonyms(synset) for synset in synsets ]))
        
        validate_bool, validated_word = self._validate_related_words(start_word, all_synonyms_start_word)
        # will later try again from scratch if no valid synonyms, refactor to reduce compute?
        second_pair_start_word = self.get_random_word_from_file()
        
        second_synsets, second_num_synsets = self.get_synsets(second_pair_start_word)
        all_synonyms_second_word = list(chain.from_iterable([ self.get_synonyms(synset) for synset in second_synsets ]))
        second_pair_validate_bool, second_pair_validated_word = self._validate_related_words(second_pair_start_word, all_synonyms_second_word)
        
        if not second_pair_validate_bool or not validate_bool:
            return self.create_synonym_question()

        else:
            # get more options which don't have this relation 
            # TODO: adjustable number of other options?
            unrelated_words = []
            while len(unrelated_words) < 3:
                word = self.get_random_word_from_file()
                # check not the same stem, and only one word, and not high partial fuzzymatch
                if self.stemmer.stem(word) != self.stemmer.stem(second_pair_validated_word) and self.stemmer.stem(word) != self.stemmer.stem(second_pair_start_word) and "_" not in word and len(word) > 0 and self._get_fuzz_score(word, second_pair_start_word) <= 95 :
                    if word not in all_synonyms_second_word: # check not also a synonym
                        unrelated_words.append(word)

            options = unrelated_words
            options.append(second_pair_validated_word)
            random.shuffle(options)

            return {"first_pair": [start_word, validated_word], "second_word": second_pair_start_word, "options": options, "correct_answer": second_pair_validated_word}

    def get_antonyms(self, lemma):
        # word = self.get_word_from_synset(synset)
        antonyms = [ str(antonym.name()) for antonym in lemma.antonyms() ]
        return antonyms

    def create_antonym_question(self) -> Dict:
        # create first pair with target relation based on random word
        start_word = self.get_random_word_from_file()
        
        synsets, num_synsets = self.get_synsets(start_word)
        lemmas = [self.get_lemma_from_synset(synset) for synset in synsets]
        # print(lemmas)
        all_antonyms_start_word = list(chain.from_iterable([ self.get_antonyms(lemma) for lemma in lemmas ]))
        print(f"ANTONYMS: {all_antonyms_start_word}")
        validate_bool, validated_word = self._validate_related_words(start_word, all_antonyms_start_word)
        # will later try again from scratch if no valid antonyms, refactor to reduce compute?
        second_pair_start_word = self.get_random_word_from_file()
        
        second_synsets, second_num_synsets = self.get_synsets(second_pair_start_word)
        second_lemmas = [self.get_lemma_from_synset(synset) for synset in second_synsets]
        all_antonyms_second_word = list(chain.from_iterable([ self.get_antonyms(lemma) for lemma in second_lemmas ]))
        second_pair_validate_bool, second_pair_validated_word = self._validate_related_words(second_pair_start_word, all_antonyms_second_word)
        
        if not second_pair_validate_bool or not validate_bool:
            return self.create_antonym_question()

        else:
            # get more options which don't have this relation 
            # TODO: adjustable number of other options?
            unrelated_words = []
            while len(unrelated_words) < 3:
                word = self.get_random_word_from_file()
                # check not the same stem, and only one word, and not high partial fuzzymatch
                if self.stemmer.stem(word) != self.stemmer.stem(second_pair_validated_word) and self.stemmer.stem(word) != self.stemmer.stem(second_pair_start_word) and "_" not in word and len(word) > 0 and self._get_fuzz_score(word, second_pair_start_word) <= 95 :
                    if word not in all_antonyms_second_word: # check not also a synonym
                        unrelated_words.append(word)
            # TODO: this fails really often i.e. need to try dozens of times to get one, add some more logic in getting words to speed that up/have antonyms ready?
            options = unrelated_words
            options.append(second_pair_validated_word)
            random.shuffle(options)

            return {"first_pair": [start_word, validated_word], "second_word": second_pair_start_word, "options": options, "correct_answer": second_pair_validated_word}

    def get_hyponyms(self, lemma):
        # word = self.get_word_from_synset(synset)
        hyponyms = lemma.hyponyms()
        return hyponyms
    
    def get_meronyms(self, lemma):
        # word = self.get_word_from_synset(synset)
        part_meronyms = lemma.part_meronyms()
        member_meronyms = lemma.member_meronyms()
        return part_meronyms + member_meronyms

    def get_holonyms(self, lemma):
        # word = self.get_word_from_synset(synset)
        part_holonyms = lemma.part_holonyms()
        member_holonyms = lemma.member_holonyms()
        return part_holonyms + member_holonyms
    
    def get_entailments(self, lemma):
        # word = self.get_word_from_synset(synset)
        entailments = lemma.entailments()
        return entailments

    # TODO/NOTE: there are more relations possible in the synset, could potentially add these/some: 
    # for reference the attributes of a lemma are (cen get with dir(lemma) ):
    # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_frame_ids', '_frame_strings', '_hypernyms', '_instance_hypernyms', '_key', '_lang', '_lex_id', '_lexname_index', '_name', '_related', '_synset', '_syntactic_marker', '_wordnet_corpus_reader', 'also_sees', 'antonyms', 'attributes', 'causes', 'count', 'derivationally_related_forms', 'entailments', 'frame_ids', 'frame_strings', 'hypernyms', 'hyponyms', 'in_region_domains', 'in_topic_domains', 'in_usage_domains', 'instance_hypernyms', 'instance_hyponyms', 'key', 'lang', 'member_holonyms', 'member_meronyms', 'name', 'part_holonyms', 'part_meronyms', 'pertainyms', 'region_domains', 'similar_tos', 'substance_holonyms', 'substance_meronyms', 'synset', 'syntactic_marker', 'topic_domains', 'usage_domains', 'verb_groups']
if __name__ == "__main__":
    maker = XIsToYMaker()
    word = maker.get_random_word()
    print(word)
    print(maker.get_synsets(word))
    synsets, num_synsets = maker.get_synsets(word)
    synset = synsets[0]
    print(f'SYNSET: {synset}')
    lemma = maker.get_lemma_from_synset(synset)
    # print(dir(lemma))
    print(f'Synonyms: {maker.get_synonyms(synset)}')
    print(f'Antonyms: {maker.get_antonyms(lemma)}')
    print(f'Hyponyms: {maker.get_hyponyms(lemma)}')
    print(f'Meronyms: {maker.get_meronyms(lemma)}')
    print(f'Holonyms: {maker.get_holonyms(synset)}')
    print(f'Entailments: {maker.get_entailments(lemma)}')
    # print(maker.create_synonym_question())
    maker._get_and_save_simple_words()