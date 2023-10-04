import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
import random
from typing import Dict, List
import json
from itertools import chain
from nltk.stem import *
from nltk.stem.porter import *
from fuzzywuzzy import fuzz
import pandas as pd
from utils import Utils
import services as _services
import models as _models

# CREATING QUESTIONS BASED ON SAVED WORD RELATIONS. CALLED FROM API #

class QuestionMaker:
    def __init__(self, length_limit: int = 1, options_num: int = 3):
        self.utils = Utils()
        self.length_limit = length_limit
        self.options_num = options_num
        
    def call_named_method(self, name: str):
        # NOTE: currently does not support passing any args to the method being called
        return getattr(self, name)()
    
    # NOTE: returning whole word obj, can then split the target column/attr and select one at random
    def get_random_word_with_relation_from_db(self, relation: str) -> _models.Word:
        return _services.get_word_with_given_relation(relation)
    
    # NOTE: here just need the word itself so not returning whole obj
    def get_random_word_from_db(self) -> str:
        return _services.get_random_word().word_name

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

    def create_synonym_question(self) -> Dict:
        # create first pair with target relation based on random word
        start_word_obj = self.get_random_word_with_relation_from_db("synonyms")
        start_pair1 = start_word_obj.word_name
        start_pair_synonyms = start_word_obj.synonyms.split(" ")
        start_pair2 = random.choice(start_pair_synonyms)

        second_word_obj = self.get_random_word_with_relation_from_db("synonyms")
        second_pair1 = second_word_obj.word_name
        second_pair_synonyms = second_word_obj.synonyms.split(" ")
        second_pair2 = random.choice(second_pair_synonyms)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word_from_db()
            if random_word not in start_pair_synonyms and random_word not in second_pair_synonyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

    def create_antonym_question(self) -> Dict:
        start_word_obj = self.get_random_word_with_relation_from_db("antonyms")
        start_pair1 = start_word_obj.word_name
        start_pair_antonyms = start_word_obj.antonyms.split(" ")
        start_pair2 = random.choice(start_pair_antonyms)

        second_word_obj = self.get_random_word_with_relation_from_db("antonyms")
        second_pair1 = second_word_obj.word_name
        second_pair_antonyms = second_word_obj.antonyms.split(" ")
        second_pair2 = random.choice(second_pair_antonyms)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word_from_db()
            if random_word not in start_pair_antonyms and random_word not in second_pair_antonyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

    def create_hyponym_question(self):
        start_word_obj = self.get_random_word_with_relation_from_db("hyponyms")
        start_pair1 = start_word_obj.word_name
        start_pair_hyponyms = start_word_obj.hyponyms.split(" ")
        start_pair2 = random.choice(start_pair_hyponyms)

        second_word_obj = self.get_random_word_with_relation_from_db("hyponyms")
        second_pair1 = second_word_obj.word_name
        second_pair_hyponyms = second_word_obj.hyponyms.split(" ")
        second_pair2 = random.choice(second_pair_hyponyms)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word_from_db()
            if random_word not in start_pair_hyponyms and random_word not in second_pair_hyponyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

    def create_meronym_question(self):
        start_word_obj = self.get_random_word_with_relation_from_db("meronyms")
        start_pair1 = start_word_obj.word_name
        start_pair_meronyms = start_word_obj.meronyms.split(" ")
        start_pair2 = random.choice(start_pair_meronyms)

        second_word_obj = self.get_random_word_with_relation_from_db("meronyms")
        second_pair1 = second_word_obj.word_name
        second_pair_meronyms = second_word_obj.meronyms.split(" ")
        second_pair2 = random.choice(second_pair_meronyms)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word_from_db()
            if random_word not in start_pair_meronyms and random_word not in second_pair_meronyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

    def create_holonym_question(self):
        start_word_obj = self.get_random_word_with_relation_from_db("holonyms")
        start_pair1 = start_word_obj.word_name
        start_pair_holonyms = start_word_obj.holonyms.split(" ")
        start_pair2 = random.choice(start_pair_holonyms)

        second_word_obj = self.get_random_word_with_relation_from_db("holonyms")
        second_pair1 = second_word_obj.word_name
        second_pair_holonyms = second_word_obj.holonyms.split(" ")
        second_pair2 = random.choice(second_pair_holonyms)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word_from_db()
            if random_word not in start_pair_holonyms and random_word not in second_pair_holonyms:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}

    def create_entailment_question(self):
        start_word_obj = self.get_random_word_with_relation_from_db("entailments")
        start_pair1 = start_word_obj.word_name
        start_pair_entailments = start_word_obj.entailments.split(" ")
        start_pair2 = random.choice(start_pair_entailments)

        second_word_obj = self.get_random_word_with_relation_from_db("entailments")
        second_pair1 = second_word_obj.word_name
        second_pair_entailments = second_word_obj.entailments.split(" ")
        second_pair2 = random.choice(second_pair_entailments)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word_from_db()
            if random_word not in start_pair_entailments and random_word not in second_pair_entailments:
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {"first_pair": [str(start_pair1), str(start_pair2)], "second_word": str(second_pair1), "options": options, "correct_answer": str(second_pair2)}