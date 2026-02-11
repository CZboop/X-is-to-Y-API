import random
from typing import Dict

import nltk

import src.db.models as _models
import src.services as _services
from src.utils import Utils

nltk.download("wordnet")

"""
 CREATING QUESTIONS BASED ON SAVED WORD RELATIONS. METHODS CALLED FROM API.
"""


class QuestionMaker:
    def __init__(self, options_num: int = 3):
        """
        Constructs an object of type QuestionMaker
        Args:
            options_num (int): The number of options to give with each question, excluding the correct answer
        """
        self.utils = Utils()
        self.options_num = options_num

    def call_named_method(self, name: str):
        """
        Calls the method passed in as an argument, which must be a method of the object calling it
        Args:
            name (str): Name of the method to be called
        Returns:
            result (dict): The result of calling the named method
        """
        # NOTE: cannot pass any args to the method being called
        try:
            return getattr(self, name)()
        except AttributeError:
            raise AttributeError(
                f"No method found called '{name}' - try one of these: 'create_antonym_question', 'create_entailment_question', 'create_holonym_question', 'create_hyponym_question', 'create_meronym_question', 'create_synonym_question'"
            )

    # NOTE: returning whole word obj, can then split the target column/attr and select one at random
    def get_random_word_with_relation_from_db(self, relation: str) -> _models.Word:
        """
        Retrieves and returns a word object (including all related words) from the database, randomly selected from the words that have at least one word related in the way passed in to the method
        Args:
            relation (str): The type of word relation that the returned word must have. Should match a column in the database
        Returns:
            word (_models.Word): A random word that has one or more words of the type of relation passed in
        """
        return _services.get_word_with_given_relation(relation)

    def get_random_word_from_db(self) -> str:
        """
        Returns a completely random word (without any of its related words) from the database
        Returns:
            word (str): A single word as a string
        """
        return _services.get_random_word().word_name

    def create_question_with_named_relation(self, relation: str) -> Dict:
        """
        Takes a string of a word relation type, returns a dict for a question using that type of word relation
        Args:
            relation (str): A type of word relation, should match the columns in the database (i.e. plural version of the relation)
        Returns:
            result (dict): A dict with the words that form the question, in the below format
            {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
        """
        # create first pair with target relation based on random word
        start_word_obj = self.get_random_word_with_relation_from_db(relation)
        start_pair1 = start_word_obj.word_name
        start_pair_relateds = getattr(start_word_obj, relation).split(" ")
        start_pair2 = random.choice(start_pair_relateds)

        second_word_obj = self.get_random_word_with_relation_from_db(relation)
        second_pair1 = second_word_obj.word_name
        second_pair_relateds = getattr(second_word_obj, relation).split(" ")
        second_pair2 = random.choice(second_pair_relateds)

        unrelated_words = []
        while len(unrelated_words) < self.options_num:
            random_word = self.get_random_word_from_db()
            if (
                random_word not in start_pair_relateds
                and random_word not in second_pair_relateds
            ):
                unrelated_words.append(random_word)

        options = unrelated_words
        options.append(second_pair2)
        random.shuffle(options)

        return {
            "first_pair": [str(start_pair1), str(start_pair2)],
            "second_word": str(second_pair1),
            "options": options,
            "correct_answer": str(second_pair2),
        }
