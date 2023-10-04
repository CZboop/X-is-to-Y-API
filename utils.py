import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
import random
from typing import Dict, List, Tuple
import json
from itertools import chain
from nltk.stem import *
from nltk.stem.porter import *
from fuzzywuzzy import fuzz
import pandas as pd

class Utils:
    def __init__(self):
        self.wn = wn
        self.words_in_wn = list(set(i for i in wn.words()))
        self.wn_length = len(self.words_in_wn)
        self.stemmer = PorterStemmer()

    def _get_fuzz_score(self, word1: str, word2: str) -> int:
        return fuzz.ratio(word1, word2)
    
    def get_random_word(self) -> str:
        random_index = random.randrange(0, self.wn_length)
        random_word = self.words_in_wn[random_index]
        return random_word
    
    def get_synsets(self, word: str) -> Tuple[List[nltk.corpus.reader.wordnet.Synset], int]:
        synset = wn.synsets(word)
        num_synsets = len(synset)
        return synset, num_synsets # note will have variable number of synsets for different words

    def get_words_from_synsets(self, synsets: List[nltk.corpus.reader.wordnet.Synset]) -> List[str]:
        lemmas = list(chain.from_iterable([synset.lemmas() for synset in synsets]))
        words = list([str(item.name()) for item in lemmas])
        return words
    
    def get_lemmas_from_synset(self, synset: nltk.corpus.reader.wordnet.Synset) -> List[nltk.corpus.reader.wordnet.Lemma]:
        lemmas = synset.lemmas()
        return lemmas

    def _validate_related_words(self, word1: str, related: List[str]) -> List[str]:
        valid_words = []
        for word in related:
            # exclude words with same stem e.g. don't want look and looked as synonyms
            if self.stemmer.stem(word) != self.stemmer.stem(word1) and self._get_fuzz_score(word, word1) <= 80:
                if not "_" in word and len(word) > 0 and word.isalpha() == True and word.lower() != word1.lower():
                    valid_words.append(word.lower())
        return valid_words