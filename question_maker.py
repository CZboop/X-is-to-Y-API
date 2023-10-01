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

    # TODO: update type hints, here def and elsewhere
    def get_random_word_with_relation(self, relation: str) -> str:
        word_df = pd.read_csv("word_details.csv")
        # TODO: later have max len used here?        
        words_with_len_and_relation = word_df.loc[word_df[relation].notnull()]
        random_word_row = words_with_len_and_relation.sample(n=1) #random select from df slice
        return random_word_row
        
    def get_random_word(self) -> str:
        word_df = pd.read_csv("word_details.csv")
        random_word = str(word_df["word"].sample(n=1).iloc[0]) #random select from series
        return random_word

    def _validate_related_words(self, word1: str, related: List[List[str]]) -> List[any]:
        # TODO: refactor to be used in the saving of words into file
        pass

    def create_synonym_question(self) -> Dict:
        # create first pair with target relation based on random word
        start_word_row = self.get_random_word_with_relation("synonyms")
        start_pair1 = start_word_row["word"].values[0]
        start_pair_synonyms = start_word_row["synonyms"].values[0].split(" ")
        start_pair2 = random.choice(start_pair_synonyms)

        second_word_row = self.get_random_word_with_relation("synonyms")
        second_pair1 = second_word_row["word"].values[0]
        second_pair_synonyms = second_word_row["synonyms"].values[0].split(" ")
        second_pair2 = random.choice(second_pair_synonyms)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word()
            if random_word not in start_pair_synonyms and random_word not in second_pair_synonyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

    def get_antonyms(self, lemma):
        # word = self.get_word_from_synset(synset)
        antonyms = [ str(antonym.name()) for antonym in lemma.antonyms() ]
        return antonyms

    def create_antonym_question(self) -> Dict:
        start_word_row = self.get_random_word_with_relation("antonyms")
        start_pair1 = start_word_row["word"].values[0]
        start_pair_antonyms = start_word_row["antonyms"].values[0].split(" ")
        start_pair2 = random.choice(start_pair_antonyms)

        second_word_row = self.get_random_word_with_relation("antonyms")
        second_pair1 = second_word_row["word"].values[0]
        second_pair_antonyms = second_word_row["antonyms"].values[0].split(" ")
        second_pair2 = random.choice(second_pair_antonyms)
        # TODO: make sure the two pairs don't overlap here?

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word()
            if random_word not in start_pair_antonyms and random_word not in second_pair_antonyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

    def create_hyponym_question(self):
        # TODO: seems none found in file, check if logic issue and/or handle here if not found
        start_word_row = self.get_random_word_with_relation("hyponyms")
        start_pair1 = start_word_row["word"].values[0]
        start_pair_hyponyms = start_word_row["hyponyms"].values[0].split(" ")
        start_pair2 = random.choice(start_pair_hyponyms)

        second_word_row = self.get_random_word_with_relation("hyponyms")
        second_pair1 = second_word_row["word"].values[0]
        second_pair_hyponyms = second_word_row["hyponyms"].values[0].split(" ")
        second_pair2 = random.choice(second_pair_hyponyms)
        # TODO: make sure the two pairs don't overlap here?

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word()
            if random_word not in start_pair_hyponyms and random_word not in second_pair_hyponyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}
    
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

    def create_entailment_question(self):
        # TODO: seems none found in file, check if logic issue and/or handle here if not found
        start_word_row = self.get_random_word_with_relation("entailments")
        start_pair1 = start_word_row["word"].values[0]
        start_pair_entailments = start_word_row["entailments"].values[0].split(" ")
        start_pair2 = random.choice(start_pair_entailments)

        second_word_row = self.get_random_word_with_relation("entailments")
        second_pair1 = second_word_row["word"].values[0]
        second_pair_entailments = second_word_row["entailments"].values[0].split(" ")
        second_pair2 = random.choice(second_pair_entailments)
        # TODO: make sure the two pairs don't overlap here?

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word()
            if random_word not in start_pair_entailments and random_word not in second_pair_entailments:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

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