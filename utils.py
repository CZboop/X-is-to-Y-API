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

'''
REUSABLE UTILS CLASS TO PASS IN TO OTHER OBJECTS
PRIMARILY VALIDATION AND RETRIEVAL OF WORDNET DATA
'''

class Utils:
    def __init__(self):
        '''
        Constructor creating an object of type Utils. Takes no args, but sets some attributes to be used in methods
        '''
        self.wn = wn
        self.words_in_wn = list(set(i for i in wn.words()))
        self.wn_length = len(self.words_in_wn)
        self.stemmer = PorterStemmer()

    def _get_fuzz_score(self, word1: str, word2: str) -> int:
        '''
        Takes two words and returns fuzzy matching score between them
        Args:
            word1 (str): First word to be compared
            word2 (str): Second word to be compared
        Returns:
            fuzz_ratio (int): Score of fuzzy similarity from 0 to 100
        '''
        return fuzz.ratio(word1, word2)
    
    def get_random_word(self) -> str:
        '''
        Returns a random word from WordNet
        Returns:
            random_word (str): A random word from wordnet
        '''
        random_index = random.randrange(0, self.wn_length)
        random_word = self.words_in_wn[random_index]
        return random_word
    
    def get_synsets(self, word: str) -> Tuple[List[nltk.corpus.reader.wordnet.Synset], int]:
        '''
        Takes a word and returns its synsets and the number of synsets it has
        Args:
            word (str): A word whose synsets we want
        Returns:
            synsets (List[nltk.corpus.reader.wordnet.Synset]): The synsets found for the word passed in
            num_synsets (int): The number of synsets found
        '''
        synsets = wn.synsets(word)
        num_synsets = len(synsets)
        return synsets, num_synsets

    def get_words_from_synsets(self, synsets: List[nltk.corpus.reader.wordnet.Synset]) -> List[str]:
        '''
        Takes a list of synsets and returns all words from the synsets
        Args:
            synsets (List[nltk.corpus.reader.wordnet.Synset]): List of synsets whose words will be returned
        Returns:
            words (List[str]): List of words found from synsets
        '''
        lemmas = list(chain.from_iterable([synset.lemmas() for synset in synsets]))
        words = list([str(item.name()) for item in lemmas])
        return words
    
    def get_lemmas_from_synset(self, synset: nltk.corpus.reader.wordnet.Synset) -> List[nltk.corpus.reader.wordnet.Lemma]:
        '''
        Takes a synset and returns its lemmas
        Args:
            synset (nltk.corpus.reader.wordnet.Synset): A synset for lemmas to be returned from
        Returns:
            lemmas (List[nltk.corpus.reader.wordnet.Lemma]): List of lemmas found from synset
        '''
        lemmas = synset.lemmas()
        return lemmas

    def _validate_related_words(self, word1: str, related: List[str]) -> List[str]:
        '''
        Takes a word and list of words related to it, returns the related words list with invalid words removed
        Args:
            word1 (str): A word to be checked against its related words
            related (List[str]): A list of related words to be validated against main word
        Returns:
            valid_words (List[str]): The original list of related words, with words removed if:
                - They are too similar to word1
                - They contain numbers
                - They contain an underscore indicating they are actually multiple words
        '''
        valid_words = []
        for word in related:
            # exclude words with same stem e.g. don't want look and looked as synonyms
            if self.stemmer.stem(word) != self.stemmer.stem(word1) and self._get_fuzz_score(word, word1) <= 80:
                if not "_" in word and len(word) > 0 and word.isalpha() == True and word.lower() != word1.lower():
                    valid_words.append(word.lower())
        return valid_words