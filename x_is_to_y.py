# Question format:
# Word1 is to (option11 option12 option13) as word2 is to (option21 option22 option23).
from nltk.corpus import wordnet as wn
import random
from typing import Dict
import json

class XIsToYMaker:
    def __init__(self, length_limit: int = 8):
        self.wn = wn
        self.words_in_wn = list(set(i for i in wn.words()))
        self.wn_length = len(self.words_in_wn)
        self.length_limit = length_limit
    
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
            if len(random_word) <= self.length_limit:
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

    def create_synonym_question(self) -> Dict:
        # create first pair with target relation based on random word
        start_word = self.get_random_word_from_file()
        
        synsets, num_synsets = self.get_synsets(start_word)
        synset = synsets[0]
        start_word_pair = self.get_synonyms(synset)
        # get another pair with the same relation

        # TODO: validation/try again if:
        # one word starts with the other/has same root
        # multiple words (underscore between)
        # scientific e.g. starts with genus_

        # get more options which don't have this relation
        return {"first_pair": [start_word, start_word_pair]}

    def get_antonyms(self, lemma):
        # word = self.get_word_from_synset(synset)
        antonyms = lemma.antonyms()
        return antonyms

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
    print(maker.create_synonym_question())
    # maker._get_and_save_simple_words()