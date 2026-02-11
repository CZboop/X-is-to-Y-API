import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
import logging
import random
from typing import Dict, List
from itertools import chain
from nltk.stem import *
from nltk.stem.porter import *
from fuzzywuzzy import fuzz
import pandas as pd
from src.utils import Utils
import src.services as _services

logger = logging.getLogger(__name__)
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s: %(funcName)s: %(levelname)s: %(message)s"
    )

'''
GET AND WRITE WORDS WITH COLUMNS OF WORDS BY TYPE OF RELATION, TO SAVE COMPUTE/RETRIES AT RUNTIME #
RUN FROM TERMINAL BEFORE API/AT STARTUP IF NOT PRESENT 
'''

class RelationWriter:
    def __init__(self, length_limit: int = 12, save_path: str = "word_details.csv", num_words: int = 100000):
        '''
        Constructs an object of type RelationWriter
        Args:
            length_limit (int): Maximum length of words to be analysed and stored
            save_path (str): Save path for word details (only used for csv, not needed for database)
            num_words (int): The total number of words to be evaluated, not all of these will be saved
        '''
        self.utils = Utils()
        self.length_limit = length_limit
        self.save_path = save_path
        self.num_words = num_words
    
    def _get_and_save_words_to_db(self) -> List[Dict[str, str]]:
        '''
        Retrieves words from WordNet, evaluates them, compiles related words and stores in the database if appropriate. Returns a list of the word details saved
        Returns:
            word_details_list (List[Dict[str, str]): A list of the dicts used as kwargs to create word objects in the database. Dict format will be as below
            {
                "word_name": str (one word), 
                "synonyms": str (space separated collection of words), 
                "antonyms": str (space separated collection of words), 
                "hyponyms": str (space separated collection of words),  
                "meronyms": str (space separated collection of words), 
                "holonyms": str (space separated collection of words), 
                "entailments": str (space separated collection of words), 
            }
        '''
        word_details_list = []
        word_names_list = []
        for word in range(self.num_words):
            random_word = self.utils.get_random_word().lower()
            # avoid duplication that db will not accept
            if random_word not in word_names_list:
                if len(random_word) <= self.length_limit and "_" not in random_word and random_word.isalpha():
                    
                    word_synsets, num_synsets = self.utils.get_synsets(random_word)
                    word_lemmas = list(chain.from_iterable([ self.utils.get_lemmas_from_synset(synset) for synset in word_synsets ]))

                    word_synonyms = self.get_synonyms(word_synsets)
                    validated_synonyms =  " ".join(self.utils._validate_related_words(random_word, word_synonyms))

                    word_antonyms = list(chain.from_iterable([ self.get_antonyms(lemma) for lemma in word_lemmas ]))
                    validated_antonyms = " ".join(self.utils._validate_related_words(random_word, word_antonyms))

                    word_hyponyms = list(chain.from_iterable(self.get_hyponyms(word_synsets)))
                    validated_hyponyms = " ".join(self.utils._validate_related_words(random_word, word_hyponyms))

                    word_meronyms = list(chain.from_iterable(self.get_meronyms(word_synsets)))
                    validated_meronyms = " ".join(self.utils._validate_related_words(random_word, word_meronyms))

                    word_holonyms = list(chain.from_iterable(self.get_holonyms(word_synsets)))
                    validated_holonyms = " ".join(self.utils._validate_related_words(random_word, word_holonyms))

                    word_entailments = list(chain.from_iterable(self.get_entailments(word_synsets)))
                    validated_entailments = " ".join(self.utils._validate_related_words(random_word, word_entailments))

                    # trimming very long lists of words to not cause psycopg2 error (150 x 12 letters should safely be under limit)
                    cols_list = [validated_synonyms, validated_antonyms, validated_hyponyms, validated_meronyms, validated_holonyms, validated_entailments]
                    for count, value in enumerate(cols_list):
                        value_split = value.split(" ")
                        if len(value_split) > 150:
                            cols_list[count] = " ".join(value_split[:150])
                    
                    # setting dict with keys and values to match db columns to be passed to create func as kwargs
                    word_details = {"word_name": random_word, "synonyms": cols_list[0], "antonyms": cols_list[1], "hyponyms": cols_list[2], "meronyms": cols_list[3], "holonyms": cols_list[4], "entailments": cols_list[5]}

                    # only save if there's something other than the original word
                    if any([len(category) > 0 for category in [validated_synonyms, validated_antonyms, validated_hyponyms, validated_meronyms, validated_holonyms, validated_entailments]]):
                        _services.create_word(word_details)
                        word_details_list.append(word_details)
                        word_names_list.append(random_word)
        logger.info(f"Added {len(word_details_list)} words and their relations to database")
        # return list of the words that should match what added to db      
        return word_details_list

    def _get_and_save_words_to_csv(self) -> pd.DataFrame:
        '''
        Retrieves words from WordNet, evaluates them, compiles related words and stores as a csv if appropriate. Returns a Pandas DataFrame of the word details saved
        Returns:
            word_details_df (pd.DataFrame): Pandas DataFrame with the following columns - ["word", "synonyms", "antonyms", "hyponyms", "meronyms", "holonyms", "entailments"]
        '''
        word_list = []
        for word in range(self.num_words):
            random_word = self.utils.get_random_word()
            if len(random_word) <= self.length_limit and "_" not in random_word and random_word.isalpha():
                
                word_synsets, num_synsets = self.utils.get_synsets(random_word)
                word_lemmas = list(chain.from_iterable([ self.utils.get_lemmas_from_synset(synset) for synset in word_synsets ]))

                word_synonyms = self.get_synonyms(word_synsets)
                validated_synonyms =  " ".join(self.utils._validate_related_words(random_word, word_synonyms))

                word_antonyms = list(chain.from_iterable([ self.get_antonyms(lemma) for lemma in word_lemmas ]))
                validated_antonyms = " ".join(self.utils._validate_related_words(random_word, word_antonyms))

                word_hyponyms = list(chain.from_iterable(self.get_hyponyms(word_synsets)))
                validated_hyponyms = " ".join(self.utils._validate_related_words(random_word, word_hyponyms))

                word_meronyms = list(chain.from_iterable(self.get_meronyms(word_synsets)))
                validated_meronyms = " ".join(self.utils._validate_related_words(random_word, word_meronyms))

                word_holonyms = list(chain.from_iterable(self.get_holonyms(word_synsets)))
                validated_holonyms = " ".join(self.utils._validate_related_words(random_word, word_holonyms))

                word_entailments = list(chain.from_iterable(self.get_entailments(word_synsets)))
                validated_entailments = " ".join(self.utils._validate_related_words(random_word, word_entailments))
                
                word_details = [random_word, validated_synonyms, validated_antonyms, validated_hyponyms, validated_meronyms, validated_holonyms, validated_entailments]

                # NOTE: lots not returning any words in any category in which case don't want to waste and save it
                if any([len(category) > 0 for category in word_details[1:]]):
                    word_list.append(word_details)

        # make list of lists into pandas dataframe
        word_details_df = pd.DataFrame(word_list, columns = ["word", "synonyms", "antonyms", "hyponyms", "meronyms", "holonyms", "entailments"])
        logger.info(f"Row number in word details - {len(word_list)}")

        # save as csv and return in df format
        word_details_df.to_csv(self.save_path)
        return word_details_df

    def get_synonyms(self, synsets: List[nltk.corpus.reader.wordnet.Synset]) -> List[str]:
        '''
        Takes a list of WordNet synsets and returns all synonyms.
        Args:
            synsets (List[nltk.corpus.reader.wordnet.Synset]): All synsets of a word as returned by the wordnet.synsets() method
        Returns:
            synonyms_lowered_unique (List[str]): All unique synonyms of synsets passed in
        '''
        words = self.utils.get_words_from_synsets(synsets)
        synonyms = list(chain.from_iterable(chain.from_iterable([wn.synonyms(word) for word in words])))
        synonyms_lowered_unique = list(set([word.lower() for word in synonyms]))
        return synonyms_lowered_unique

    def get_antonyms(self, lemma: nltk.corpus.reader.wordnet.Lemma) -> List[str]:
        '''
        Takes a lemma and returns a list of its antonyms
        Args:
            lemma (nltk.corpus.reader.wordnet.Lemma): A WordNet lemma of the word whose antonyms are being found
        Returns:
            antonyms (List[str]): Antonyms of the lemma
        '''
        antonyms = [ str(antonym.name()) for antonym in lemma.antonyms() ]
        return antonyms

    def get_hyponyms(self, synsets: List[nltk.corpus.reader.wordnet.Synset]) -> List[str]:
        '''
        Takes a list of synsets and returns a list of hyponyms
        Args:
            synsets (List[nltk.corpus.reader.wordnet.Synset]): All synsets of a word as returned by the wordnet.synsets() method
        Returns:
            hyponym_words (List[str]): A lits of all hyponyms from the synsets passed in as args
        '''
        hyponyms = [synset.hyponyms() for synset in synsets]
        hyponym_words = [self.utils.get_words_from_synsets(synset) for synset in hyponyms]
        return hyponym_words
    
    def get_meronyms(self, synsets: List[nltk.corpus.reader.wordnet.Synset]) -> List[str]:
        '''
        Takes a list of synsets and returns all member meronyms and part meronyms as one list of strings
        Args:
            synsets (List[nltk.corpus.reader.wordnet.Synset]): A list of synsets for the word whose meronyms we want to find
        Returns:
            meronym_words (List[str]): All member and part meronyms for the synsets from args
        '''
        part_meronyms = [synset.part_meronyms() for synset in synsets]
        member_meronyms = [synset.member_meronyms() for synset in synsets]
        all_meronyms = part_meronyms + member_meronyms
        meronym_words = [self.utils.get_words_from_synsets(synset) for synset in all_meronyms]
        return meronym_words

    def get_holonyms(self, synsets: List[nltk.corpus.reader.wordnet.Synset]) -> List[str]:
        '''
        Takes a list of synsets and returns all member holonyms and part holonyms as one list of strings
        Args:
            synsets (List[nltk.corpus.reader.wordnet.Synset]): A list of synsets for the word whose holonyms we want to find
        Returns:
            holonym_words (List[str]): All member and part holonyms for the synsets from args
        '''
        part_holonyms = [synset.part_holonyms() for synset in synsets]
        member_holonyms = [synset.member_holonyms() for synset in synsets]
        all_holonyms = part_holonyms + member_holonyms
        holonym_words = [self.utils.get_words_from_synsets(synset) for synset in all_holonyms]
        return holonym_words
    
    def get_entailments(self, synsets: List[nltk.corpus.reader.wordnet.Synset]) -> List[str]:
        '''
        Takes a list of synsets and returns all entailments for those synsets
        Args:
            synsets (List[nltk.corpus.reader.wordnet.Synset]): A list of synsets for the word whose holonyms we want to find
        Returns:
            entailments_words (List[str]): All entailments for the synsets from args
        '''
        entailments = [synset.entailments() for synset in synsets]
        entailments_words = [self.utils.get_words_from_synsets(synset) for synset in entailments]
        return entailments_words

    def run(self, save_method: str = "csv"):
        '''
        Takes a save method and creates word relations in csv or database format
        Args:
            save_method (str): Whether to save in csv or database format. Should be "csv" for csv or anything else for database
        '''
        if save_method == "csv":
            self._get_and_save_words_to_csv()
        else:
            self._get_and_save_words_to_db()