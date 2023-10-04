import unittest, pytest
from utils import Utils
from pathlib import Path
import os
import shutil
from nltk.corpus import wordnet as wn
import nltk

class TestUtils(unittest.TestCase):

    maxDiff = None

    # == TEST GET RANDOM WORD == #

    def test_get_random_word_returns_a_string_found_in_wordnet_word_list(self):
        # given - an instance of the utils class and wordnet words list
        undertest_class = Utils()
        wordnet = wn.words()

        # when - we call the get random word method of the utils class
        actual_word = undertest_class.get_random_word()

        # then - the returned value is type string, with value found in the wordnet
        self.assertTrue(type(actual_word) == str)
        self.assertTrue(actual_word in wordnet)

    def test_get_random_word_returns_two_different_words_when_called_twice(self):
        # given - an instance of the utils class
        undertest_class = Utils()

        # when - we call the get random word method of the utils class twice
        actual_word1 = undertest_class.get_random_word()
        actual_word2 = undertest_class.get_random_word()

        # then - the words returned are not the same
        self.assertNotEqual(actual_word1, actual_word2)

    # == TEST GET SYNSETS == #
    def test_get_synsets_returns_list_of_synsets_and_number_of_synsets(self):
        # given - an instance of the utils class
        undertest_class = Utils()

        # when - we call the get_synsets method, passing in a common word that can be found in wordnet with multiple synsets
        actual_synsets, actual_num_synsets = undertest_class.get_synsets("class")

        # then - returned values are of the expected types
        self.assertTrue(type(actual_synsets) == list)
        self.assertTrue(type(actual_num_synsets) == int)

    # == TEST GET WORDS FROM SYNSETS == #

    # == TEST GET LEMMAS FROM SYNSET == #

    # == TEST VALIDATE RELATED WORDS == #

if __name__ == "__main__":
    unittest.main()