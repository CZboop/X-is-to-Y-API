import sqlalchemy as _sql
import db as _db

class Word(_db.Base):
    __tablename__ = "words"
    id = _sql.Column(_sql.Integer, primary_key = True, index = True)
    word_name = _sql.Column(_sql.String, index = True, unique = True)
    synonyms = _sql.Column(_sql.String, index = True)
    antonyms = _sql.Column(_sql.String, index = True)
    holonyms = _sql.Column(_sql.String, index = True)
    meronyms = _sql.Column(_sql.String, index = True)
    hyponyms = _sql.Column(_sql.String, index = True)
    entailments = _sql.Column(_sql.String, index = True)