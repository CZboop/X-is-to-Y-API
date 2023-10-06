import sqlalchemy as _sql
import db.database as _db

class Word(_db.Base):
    '''
    Creates an entry in the connected "words" SQL table with column values from the given args.
    Args:
        word_name (str): The word itself
        synonyms (str): Synonyms of the word (1 or more words separated by spaces)
        antonyms (str): Antonyms of the word (1 or more words separated by spaces)
        holonyms (str): Holonyms of the word (1 or more words separated by spaces)
        meronyms (str): Meronyms of the word (1 or more words separated by spaces)
        hyponyms (str): Hyponyms of the word (1 or more words separated by spaces)
        entailments (str): Entailments of the word (1 or more words separated by spaces)
    '''
    __tablename__ = "words"
    id = _sql.Column(_sql.Integer, primary_key = True, index = True)
    word_name = _sql.Column(_sql.String, index = True, unique = True)
    synonyms = _sql.Column(_sql.String, index = True)
    antonyms = _sql.Column(_sql.String, index = True)
    holonyms = _sql.Column(_sql.String, index = True)
    meronyms = _sql.Column(_sql.String, index = True)
    hyponyms = _sql.Column(_sql.String, index = True)
    entailments = _sql.Column(_sql.String, index = True)