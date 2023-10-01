from nltk.corpus import wordnet as wn
import random
from typing import Dict, List
import json
from itertools import chain
from nltk.stem import *
from nltk.stem.porter import *
from fuzzywuzzy import fuzz
import pandas as pd

# CREATING QUESTIONS BASED ON SAVED WORD RELATIONS. CALLED FROM API #

class QuestionMaker:
    def __init__(self, length_limit: int = 1, options_num: int = 3):
        self.wn = wn
        self.words_in_wn = list(set(i for i in wn.words()))
        self.wn_length = len(self.words_in_wn)
        self.length_limit = length_limit
        self.options_num = options_num
        self.stemmer = PorterStemmer()

    def call_named_method(self, name: str):
        # NOTE: currently does not support passing any args to the method being called
        return getattr(self, name)()

    # TODO: refactor these type of methods into utils if using in multi files
    def _get_fuzz_score(self, word1: str, word2: str) -> int:
        return fuzz.partial_ratio(word1, word2)

    def get_synsets(self, word: str):
        synset = wn.synsets(word)
        num_synsets = len(synset)
        return synset, num_synsets # note will have variable number of synsets for different words

    def get_word_from_synset(self, synset):
        # TODO: could do some shuffling of lemmas?
        word = str(synset.lemmas()[0].name())
        return word
    
    def get_lemmas_from_synset(self, synset):
        # TODO: refactor now that returning all lemmas not just first
        lemmas = synset.lemmas()
        return lemmas

    # TODO: get synonyms, antonyms, hyponym, meronym (larger or smaller of given category), troponym (way of doing the thing), entailment (x entails y, prerequisite/one implies another)
    def get_synonyms(self, synset):
        word = self.get_word_from_synset(synset)
        synonyms = wn.synonyms(word)
        return synonyms

    # TODO: update type hints, here def and elsewhere
    def get_random_word_with_relation(self, relation: str) -> str:
        word_df = pd.read_csv("word_details.csv")
        # TODO: later have max len used here?
        word_df['word'] = word_df['word'].astype('str')
        filter_mask = len(word_df[relation]) > 0 # or is there a better null check?
        
        words_with_len_and_relation = word_df.loc[filter_mask]
        random_word_row = words_with_len_and_relation.sample(n=1) #random select from df slice
        return random_word_row
        
    def get_random_word(self) -> str:
        word_df = pd.read_csv("word_details.csv")
        random_word = word_df["word"].sample(n=1) #random select from series
        return random_word

    def _validate_related_words(self, word1: str, related: List[List[str]]) -> List[any]:
        # TODO: refactor to be used in the saving of words into file
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
        start_word_row = self.get_random_word_with_relation("synonyms")
        start_pair1 = start_word_row["word"]
        start_pair_synonyms = start_word_row["synonyms"] # TODO: proper list and select
        start_pair2 = random.choice(start_pair_synonyms)

        second_word_row = self.get_random_word_with_relation("synonyms")
        second_pair1 = second_word_row["word"]
        second_pair_synonyms = second_word_row["synonyms"] # TODO: proper list and select
        second_pair2 = random.choice(second_pair_synonyms)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word()
            if random_word not in start_pair_synonyms and random_word not in second_pair_synonyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [start_pair1, start_pair1], "second_word": second_pair1, "options": options, "correct_answer": second_pair2}

    def get_antonyms(self, lemma):
        # word = self.get_word_from_synset(synset)
        antonyms = [ str(antonym.name()) for antonym in lemma.antonyms() ]
        return antonyms

    def create_antonym_question(self) -> Dict:
        # create first pair with target relation based on random word
        start_word = self.get_random_word_from_file()
        
        synsets, num_synsets = self.get_synsets(start_word)
        lemmas = [self.get_lemmas_from_synset(synset) for synset in synsets]
        # print(lemmas)
        all_antonyms_start_word = list(chain.from_iterable([ self.get_antonyms(lemma) for lemma in lemmas ]))
        print(f"ANTONYMS: {all_antonyms_start_word}")
        validate_bool, validated_word = self._validate_related_words(start_word, all_antonyms_start_word)
        # will later try again from scratch if no valid antonyms, refactor to reduce compute?
        second_pair_start_word = self.get_random_word_from_file()
        
        second_synsets, second_num_synsets = self.get_synsets(second_pair_start_word)
        second_lemmas = [self.get_lemmas_from_synset(synset) for synset in second_synsets]
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

    def create_hyponym_question(self):
        # create first pair with target relation based on random word
        start_word = self.get_random_word_from_file()
        
        synsets, num_synsets = self.get_synsets(start_word)
        lemmas = [self.get_lemmas_from_synset(synset) for synset in synsets]
        # print(lemmas)
        all_hyponyms_start_word = list(chain.from_iterable([ self.get_hyponyms(lemma) for lemma in lemmas ]))
        print(f"HYPONYMS: {all_hyponyms_start_word}")
        validate_bool, validated_word = self._validate_related_words(start_word, all_hyponyms_start_word)
        # will later try again from scratch if no valid hyponyms, refactor to reduce compute?
        second_pair_start_word = self.get_random_word_from_file()
        
        second_synsets, second_num_synsets = self.get_synsets(second_pair_start_word)
        second_lemmas = [self.get_lemmas_from_synset(synset) for synset in second_synsets]
        all_hyponyms_second_word = list(chain.from_iterable([ self.get_hyponyms(lemma) for lemma in second_lemmas ]))
        second_pair_validate_bool, second_pair_validated_word = self._validate_related_words(second_pair_start_word, all_hyponyms_second_word)
        
        if not second_pair_validate_bool or not validate_bool:
            return self.create_hyponym_question()

        else:
            # get more options which don't have this relation 
            # TODO: adjustable number of other options?
            unrelated_words = []
            while len(unrelated_words) < 3:
                word = self.get_random_word_from_file()
                # check not the same stem, and only one word, and not high partial fuzzymatch
                if self.stemmer.stem(word) != self.stemmer.stem(second_pair_validated_word) and self.stemmer.stem(word) != self.stemmer.stem(second_pair_start_word) and "_" not in word and len(word) > 0 and self._get_fuzz_score(word, second_pair_start_word) <= 95 :
                    if word not in all_hyponyms_second_word: # check not also a synonym
                        unrelated_words.append(word)
            # TODO: unusably slow - for hyponym needs to be made, stored and pulled rather than made at runtime/ combine with meronyms and holonyms?
            options = unrelated_words
            options.append(second_pair_validated_word)
            random.shuffle(options)

            return {"first_pair": [start_word, validated_word], "second_word": second_pair_start_word, "options": options, "correct_answer": second_pair_validated_word}
    
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

    def create_entailment_question(self):
        # create first pair with target relation based on random word
        start_word = self.get_random_word_from_file()
        
        synsets, num_synsets = self.get_synsets(start_word)
        lemmas = [self.get_lemmas_from_synset(synset) for synset in synsets]
        # print(lemmas)
        all_entailments_start_word = list(chain.from_iterable([ self.get_entailments(lemma) for lemma in lemmas ]))
        print(f"ENTAILMENTS: {all_entailments_start_word}")
        validate_bool, validated_word = self._validate_related_words(start_word, all_entailments_start_word)
        # will later try again from scratch if no valid entailments, refactor to reduce compute?
        second_pair_start_word = self.get_random_word_from_file()
        
        second_synsets, second_num_synsets = self.get_synsets(second_pair_start_word)
        second_lemmas = [self.get_lemmas_from_synset(synset) for synset in second_synsets]
        all_entailments_second_word = list(chain.from_iterable([ self.get_entailments(lemma) for lemma in second_lemmas ]))
        second_pair_validate_bool, second_pair_validated_word = self._validate_related_words(second_pair_start_word, all_entailments_second_word)
        
        if not second_pair_validate_bool or not validate_bool:
            return self.create_entailment_question()

        else:
            # get more options which don't have this relation 
            # TODO: adjustable number of other options?
            unrelated_words = []
            while len(unrelated_words) < 3:
                word = self.get_random_word_from_file()
                # check not the same stem, and only one word, and not high partial fuzzymatch
                if self.stemmer.stem(word) != self.stemmer.stem(second_pair_validated_word) and self.stemmer.stem(word) != self.stemmer.stem(second_pair_start_word) and "_" not in word and len(word) > 0 and self._get_fuzz_score(word, second_pair_start_word) <= 95 :
                    if word not in all_entailments_second_word: # check not also a synonym
                        unrelated_words.append(word)
            # TODO: again unusably slow for making at runtime, needs diff method when saving words add some info, load into df and select?
            options = unrelated_words
            options.append(second_pair_validated_word)
            random.shuffle(options)

            return {"first_pair": [start_word, validated_word], "second_word": second_pair_start_word, "options": options, "correct_answer": second_pair_validated_word}

    # TODO: relations to try adding (BASED ON ATTRS) also_sees, attributes?, in_topic_domains, in_usage_domains, partainyms, similar_tos, verb_groups: ONCE WORD GET LOGIC IRONED OUT...

    # TODO/NOTE: there are more relations possible in the synset, could potentially add some,
    # (can get attrs with dir(lemma) ):
if __name__ == "__main__":
    maker = QuestionMaker()
    # word = maker.get_random_word()
    # print(word)
    
    print(maker.get_synsets(word))
    synsets, num_synsets = maker.get_synsets(word)
    synset = synsets[0]
    print(f'SYNSET: {synset}')
    lemma = maker.get_lemmas_from_synset(synset)
    # print(dir(lemma))
    print(f'Synonyms: {maker.get_synonyms(synset)}')
    print(f'Antonyms: {maker.get_antonyms(lemma)}')
    print(f'Hyponyms: {maker.get_hyponyms(lemma)}')
    print(f'Meronyms: {maker.get_meronyms(lemma)}')
    print(f'Holonyms: {maker.get_holonyms(synset)}')
    print(f'Entailments: {maker.get_entailments(lemma)}')
    # print(maker.create_synonym_question())
    maker._get_and_save_words()