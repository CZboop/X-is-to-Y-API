import random
from typing import TYPE_CHECKING, Dict, List

from fastapi import HTTPException
from sqlalchemy.sql.expression import func

import src.db.database as _db
import src.db.models as _models
import src.db.schemas as _schemas

if TYPE_CHECKING:
    pass

"""
FUNCTIONS TO INTERACT WITH THE DATABASE
"""


def _setup_tables():
    """
    Creates the "words" table based on declarative base model
    """
    return _db.Base.metadata.create_all(bind=_db.engine)


def create_word(word: Dict[str, str]) -> _schemas.Word:
    """
    Adds a word object to the database from a dict of properties
    Args:
        word (Dict[str, str]): Dict of kwargs to be passed as properties to word constructor
    Returns:
        word (_schemas.Word): Word based on pydantic base model
    """
    word = _models.Word(**word)
    db = _db.SessionLocal()

    db.add(word)
    db.commit()
    db.refresh(word)
    db.close()

    return _schemas.Word.from_orm(word)


def get_word_with_given_relation(relation: str) -> _schemas.Word:
    """
    Takes a string of word relation and returns an object representing a row from the word table, which has words with that relation
    Args:
        relation (str): String to be checked as being not null when selecting a random word, should match a column in the word table
    Returns:
        random_word (_schemas.Word): Word object created from a row in the words table, randomly selected from words with the given relation
    """
    db = _db.SessionLocal()
    words_with_relation = db.query(_models.Word).filter(
        getattr(_models.Word, relation) != ""
    )
    random_word = words_with_relation.order_by(func.random()).first()
    db.close()
    if random_word is None:
        raise HTTPException(
            status_code=404, detail=f"No words with {relation} found :("
        )

    return random_word


def get_random_word() -> _schemas.Word:
    """
    Returns a word object created from a completely random word in the database
    Returns:
        random_word (_schemas.Word): A random word from the "words" table as a word object
    """
    db = _db.SessionLocal()
    try:
        random_word = random.choice(db.query(_models.Word).all())
    except IndexError:
        raise HTTPException(status_code=404, detail="No words found :(")
    finally:
        db.close()
    return random_word


def get_all_words() -> List[_schemas.Word]:
    """
    Returns all words from the database
    Returns:
        all_words (List[_schemas.Word]): A list of word objects representing every word in the "words" table
    """
    db = _db.SessionLocal()
    all_words = db.query(_models.Word).all()
    db.close()
    return all_words
