from nltk.corpus import wordnet as wn
import random
from typing import Dict, List
import json
from itertools import chain
from nltk.stem import *
from nltk.stem.porter import *
from fuzzywuzzy import fuzz
import pandas as pd

# GET AND WRITE WORDS WITH COLUMNS OF WORDS BY TYPE OF RELATION, TO SAVE COMPUTE/RETRIES AT RUNTIME #
# RUN FROM TERMINAL BEFORE API/AT STARTUP IF NOT PRESENT #

class RelationWriter:
    def __init__(self, length_limit: int = 12):
        self.wn = wn
        self.words_in_wn = list(set(i for i in wn.words()))
        self.wn_length = len(self.words_in_wn)
        self.length_limit = length_limit
        self.stemmer = PorterStemmer()
    
    def _get_fuzz_score(self, word1: str, word2: str) -> int:
        return fuzz.ratio(word1, word2)
    
    # NOTE: random words will lean towards very obscure words, some form of filtering or starting word set that is narrowed and more common
    def get_random_word(self) -> str:
        random_index = random.randrange(0, self.wn_length)
        random_word = self.words_in_wn[random_index]
        return random_word
    
    def _get_and_save_words(self, num_words: int = 25000):
        # method to get lots of words and save the ones that are below certain length or simplicity (look into methods for readability of single word?)
        word_list = []
        # TODO: get info and for each word append a list to word_list, then make df passing in column names
        for word in range(num_words):
            random_word = self.get_random_word()
            if len(random_word) <= self.length_limit and "_" not in random_word and random_word.isalpha():
                
                word_synsets, num_synsets = self.get_synsets(random_word)
                word_lemmas = list(chain.from_iterable([ self.get_lemmas_from_synset(synset) for synset in word_synsets ]))

                word_synonyms = self.get_synonyms(word_synsets)
                validated_synonyms =  " ".join(self._validate_related_words(random_word, word_synonyms))

                word_antonyms = list(chain.from_iterable([ self.get_antonyms(lemma) for lemma in word_lemmas ]))
                validated_antonyms = " ".join(self._validate_related_words(random_word, word_antonyms))

                word_hyponyms = list(chain.from_iterable([ self.get_hyponyms(lemma) for lemma in word_lemmas ]))
                validated_hyponyms = " ".join(self._validate_related_words(random_word, word_hyponyms))

                word_meronyms = list(chain.from_iterable([ self.get_meronyms(lemma) for lemma in word_lemmas ]))
                validated_meronyms = " ".join(self._validate_related_words(random_word, word_meronyms))

                word_holonyms = list(chain.from_iterable([ self.get_holonyms(lemma) for lemma in word_lemmas ]))
                validated_holonyms = " ".join(self._validate_related_words(random_word, word_holonyms))

                word_entailments = list(chain.from_iterable([ self.get_entailments(lemma) for lemma in word_lemmas ]))
                validated_entailments = " ".join(self._validate_related_words(random_word, word_entailments))
                
                word_details = [random_word, validated_synonyms, validated_antonyms, validated_hyponyms, validated_meronyms, validated_holonyms, validated_entailments]
                # NOTE: lots not returning any words in any category in which case don't want to waste and save it
                if any([len(category) > 0 for category in word_details[1:]]):
                    word_list.append(word_details)
        word_details_df = pd.DataFrame(word_list, columns = ["word", "synonyms", "antonyms", "hyponyms", "meronyms", "holonyms", "entailments"])
        print(len(word_list))
        word_details_df.to_csv("word_details.csv")
        # TODO: read in existing data and append ?
        return word_details_df

    def get_synsets(self, word: str):
        synset = wn.synsets(word)
        num_synsets = len(synset)
        return synset, num_synsets # note will have variable number of synsets for different words

    def get_words_from_synsets(self, synsets):
        lemmas = list(chain.from_iterable([synset.lemmas() for synset in synsets]))
        print(lemmas)
        words = list([str(item.name()) for item in lemmas])
        print(words)
        return words
    
    def get_lemmas_from_synset(self, synset):
        lemmas = synset.lemmas()
        return lemmas

    def get_synonyms(self, synset):
        words = self.get_words_from_synsets(synset)
        synonyms = list(chain.from_iterable(chain.from_iterable([wn.synonyms(word) for word in words])))
        print(f"SYNONYMS: {synonyms}")
        synonyms_lowered_unique = list(set([word.lower() for word in synonyms]))
        return synonyms_lowered_unique

    def _validate_related_words(self, word1: str, related: List[List[str]]) -> List[any]:
        # TODO: refactor to be used in the saving of words into file
        if len(related) > 0 and type(related[0]) == list:
            related_chained = list(chain.from_iterable(related))
        else:
            related_chained = related
        valid_words = []
        for word in related_chained:
            # exclude words with same stem e.g. don't want look and looked as synonyms
            if self.stemmer.stem(word) != self.stemmer.stem(word1) and self._get_fuzz_score(word, word1) <= 90:
                if not "_" in word and len(word) > 0 and word.isalpha() == True:
                    valid_words.append(word)
        return valid_words

    def get_antonyms(self, lemma):
        antonyms = [ str(antonym.name()) for antonym in lemma.antonyms() ]
        return antonyms

    def get_hyponyms(self, lemma):
        hyponyms = lemma.hyponyms()
        return hyponyms
    
    def get_meronyms(self, lemma):
        part_meronyms = lemma.part_meronyms()
        member_meronyms = lemma.member_meronyms()
        return part_meronyms + member_meronyms

    def get_holonyms(self, lemma):
        part_holonyms = lemma.part_holonyms()
        member_holonyms = lemma.member_holonyms()
        return part_holonyms + member_holonyms
    
    def get_entailments(self, lemma):
        entailments = lemma.entailments()
        return entailments

    def run(self):
        self._get_and_save_words()

if __name__ == "__main__":
    relation_writer = RelationWriter()

    # random_word = relation_writer.get_random_word()
    # word_synsets, num_synsets = relation_writer.get_synsets(random_word)

    # relation_writer.get_words_from_synsets(word_synsets)
    relation_writer.run()

