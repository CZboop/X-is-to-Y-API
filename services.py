import database as _db
import models as _models
import schemas as _schemas
from typing import TYPE_CHECKING, List
from sqlalchemy.sql.expression import func, select
import random

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

    return _schemas.Word.from_orm(word)

def get_word_with_given_relation(relation: str) -> _schemas.Word:
    db = _db.SessionLocal()
    words_with_relation = db.query(_models.Word).filter(getattr(_models.Word, relation) != "")
    random_word = words_with_relation.order_by(func.random()).first()

    return random_word

def get_random_word() -> _schemas.Word:
    db = _db.SessionLocal()
    random_word = random.choice(db.query(_models.Word).all())

    return random_word

if __name__ == "__main__":
    _setup_tables()