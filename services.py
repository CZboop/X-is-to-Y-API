import database as _db
import models as _models
import schemas as _schemas
from typing import TYPE_CHECKING, List
from sqlalchemy.sql.expression import func, select
import random
from fastapi import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def _setup_tables():
    return _db.Base.metadata.create_all(bind = _db.engine)

def get_db():
    db = _db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_word(word: _schemas.CreateWord) -> _schemas.Word:
    word = _models.Word(**word) # unpacking dict passed in as kwargs
    db = _db.SessionLocal()

    db.add(word)
    db.commit()
    db.refresh(word)
    db.close()
    
    return _schemas.Word.from_orm(word)

def get_word_with_given_relation(relation: str) -> _schemas.Word:
    db = _db.SessionLocal()
    words_with_relation = db.query(_models.Word).filter(getattr(_models.Word, relation) != "")
    random_word = words_with_relation.order_by(func.random()).first()
    db.close()
    if random_word == None:
        raise HTTPException(status_code=404, detail=f"No words with {relation} found :(")

    return random_word

def get_random_word() -> _schemas.Word:
    db = _db.SessionLocal()
    try:
        random_word = random.choice(db.query(_models.Word).all())
    except IndexError:
        raise HTTPException(status_code=404, detail=f"No words found :(")
    finally:
        db.close()
    return random_word

def get_all_words() -> List[_schemas.Word]:
    db = _db.SessionLocal()
    all_words = db.query(_models.Word).all()
    db.close()
    return all_words

if __name__ == "__main__":
    _setup_tables()