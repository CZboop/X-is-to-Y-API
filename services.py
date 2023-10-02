import db as _db
import models as _models

def _setup_tables():
    return _db.Base.metadata.create_all(bind = _db.engine)

if __name__ == "__main__":
    _setup_tables()