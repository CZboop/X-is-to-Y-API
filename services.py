import database as _db
import models as _models
import schemas as _schemas
from typing import TYPE_CHECKING

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

def create_word(word: _schemas.CreateWord, db: "Session") -> _schemas.Word:
    word = _models.Word(**word.dict()) # pass in as kwargs dict and it will unpack
    db.add(word)
    db.commit()
    db.refresh(word)
    return _schemas.Word.from_orm(word)

if __name__ == "__main__":
    _setup_tables()