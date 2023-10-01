from nltk.corpus import wordnet as wn
import nltk
import logging
import random
from typing import Dict, List
from itertools import chain
from nltk.stem import *
from nltk.stem.porter import *
from fuzzywuzzy import fuzz
import pandas as pd
from utils import Utils

logger = logging.getLogger(__name__)
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s: %(funcName)s: %(levelname)s: %(message)s"
    )

# GET AND WRITE WORDS WITH COLUMNS OF WORDS BY TYPE OF RELATION, TO SAVE COMPUTE/RETRIES AT RUNTIME #
# RUN FROM TERMINAL BEFORE API/AT STARTUP IF NOT PRESENT #

class RelationWriter:
    def __init__(self, length_limit: int = 12, save_path: str = "word_details.csv"):
        self.utils = Utils()
        self.length_limit = length_limit
        self.save_path = save_path

    def _get_and_save_words(self, num_words: int = 5000) -> pd.DataFrame:
        word_list = []
        for word in range(num_words):
            random_word = self.utils.get_random_word()
            if len(random_word) <= self.length_limit and "_" not in random_word and random_word.isalpha():
                
                word_synsets, num_synsets = self.utils.get_synsets(random_word)
                word_lemmas = list(chain.from_iterable([ self.utils.get_lemmas_from_synset(synset) for synset in word_synsets ]))

                word_synonyms = self.get_synonyms(word_synsets)
                validated_synonyms =  " ".join(self.utils._validate_related_words(random_word, word_synonyms))

                word_antonyms = list(chain.from_iterable([ self.get_antonyms(lemma) for lemma in word_lemmas ]))
                validated_antonyms = " ".join(self.utils._validate_related_words(random_word, word_antonyms))

                word_hyponyms = list(chain.from_iterable([ self.get_hyponyms(lemma) for lemma in word_lemmas ]))
                validated_hyponyms = " ".join(self.utils._validate_related_words(random_word, word_hyponyms))

                word_meronyms = list(chain.from_iterable([ self.get_meronyms(lemma) for lemma in word_lemmas ]))
                validated_meronyms = " ".join(self.utils._validate_related_words(random_word, word_meronyms))

                word_holonyms = list(chain.from_iterable(self.get_holonyms(word_synsets)))
                validated_holonyms = " ".join(self.utils._validate_related_words(random_word, word_holonyms))

                word_entailments = list(chain.from_iterable([ self.get_entailments(lemma) for lemma in word_lemmas ]))
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
        # TODO: read in existing data and append ?
        return word_details_df

    def get_synonyms(self, synsets: List[nltk.corpus.reader.wordnet.Synset]):
        words = self.utils.get_words_from_synsets(synsets)
        synonyms = list(chain.from_iterable(chain.from_iterable([wn.synonyms(word) for word in words])))
        synonyms_lowered_unique = list(set([word.lower() for word in synonyms]))
        return synonyms_lowered_unique

    def get_antonyms(self, lemma: nltk.corpus.reader.wordnet.Lemma):
        antonyms = [ str(antonym.name()) for antonym in lemma.antonyms() ]
        return antonyms

    def get_hyponyms(self, lemma: nltk.corpus.reader.wordnet.Lemma):
        hyponyms = lemma.hyponyms()
        return hyponyms
    
    def get_meronyms(self, lemma: nltk.corpus.reader.wordnet.Lemma):
        part_meronyms = lemma.part_meronyms()
        member_meronyms = lemma.member_meronyms()
        return part_meronyms + member_meronyms

    def get_holonyms(self, synsets: nltk.corpus.reader.wordnet.Synset):
        part_holonyms = [synset.part_holonyms() for synset in synsets]
        member_holonyms = [synset.member_holonyms() for synset in synsets]
        all_holonyms = part_holonyms + member_holonyms
        holonym_words = [self.utils.get_words_from_synsets(synset) for synset in all_holonyms]
        return holonym_words
    
    def get_entailments(self, lemma: nltk.corpus.reader.wordnet.Lemma):
        entailments = lemma.entailments()
        return entailments

    def run(self):
        self._get_and_save_words()

if __name__ == "__main__":
    relation_writer = RelationWriter(save_path = "test.csv")
    synset = relation_writer.run()