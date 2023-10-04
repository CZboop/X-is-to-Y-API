import unittest, pytest
from schemas import _BaseWord

class TestSchemas(unittest.TestCase):

    maxDiff = None

    # == TEST CREATING WORD OBJECT FROM BASE MODEL == #

    def test_can_create_word_object_with_kwargs_dict(self):
        # given - a dict object with an entry for each attribute of the word model
        word_kwargs = {"word_name": "synonym", "synonyms": "term", "antonyms": "antonym", "holonyms": "language", "meronyms": "semantics", "hyponyms": "super-synonym", "entailments": "word"}

        # when - we call the constructor passing in the dict with word info as kwargs
        word = _BaseWord(**word_kwargs)

        # then - a word object is successfully created with the expected properties
        self.assertEqual(word.word_name, "synonym")
        self.assertEqual(word.synonyms, "term")
        self.assertEqual(word.antonyms, "antonym")
        self.assertEqual(word.holonyms, "language")
        self.assertEqual(word.meronyms, "semantics")
        self.assertEqual(word.hyponyms, "super-synonym")
        self.assertEqual(word.entailments, "word")

    def test_can_create_word_object_with_explicit_properties(self):
        # given - variables for each attribute of the word model
        word_name = "synonym" 
        synonyms = "term"
        antonyms = "antonym"
        holonyms = "language" 
        meronyms = "semantics" 
        hyponyms = "super-synonym" 
        entailments = "word"

        # when - we call the constructor passing in each variable for each attribute

        word = _BaseWord(word_name = word_name, synonyms = synonyms, antonyms = antonyms, holonyms = holonyms, meronyms = meronyms, hyponyms = hyponyms, entailments = entailments)

        # then - a word object is successfully created with the expected properties
        self.assertEqual(word.word_name, "synonym")
        self.assertEqual(word.synonyms, "term")
        self.assertEqual(word.antonyms, "antonym")
        self.assertEqual(word.holonyms, "language")
        self.assertEqual(word.meronyms, "semantics")
        self.assertEqual(word.hyponyms, "super-synonym")
        self.assertEqual(word.entailments, "word")

if __name__ == "__main__":
    unittest.main()