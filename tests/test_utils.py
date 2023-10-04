import unittest, pytest
from utils import Utils
from pathlib import Path
import os
import shutil
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn

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
    def test_get_words_from_synsets_returns_a_list_of_strings(self):
        # given - an instance of the utils class
        undertest_class = Utils()

        # when - we call the get words from synsets method passing in a list of synsets
        actual_synsets, _ = undertest_class.get_synsets("class")
        actual_words = undertest_class.get_words_from_synsets(actual_synsets)

        # then - a list of strings is returned
        self.assertTrue(type(actual_words) == list)
        self.assertTrue(all([type(i) == str for i in actual_words]))

    # == TEST GET LEMMAS FROM SYNSET == #
    def test_get_lemmas_from_synset_returns_list_of_lemmas(self):
        # given - an instance of the utils class
        undertest_class = Utils()

        # when - we call the get lemmas from synsets method passing in a synset
        actual_synsets, _ = undertest_class.get_synsets("class")
        actual_words = undertest_class.get_lemmas_from_synset(actual_synsets[0])

        # then - a list of strings is returned
        self.assertTrue(type(actual_words) == list)
        self.assertTrue(all([type(i) == nltk.corpus.reader.wordnet.Lemma for i in actual_words]))

    # == TEST VALIDATE RELATED WORDS == #

if __name__ == "__main__":
    unittest.main()