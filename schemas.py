import pydantic as _pydantic

class _BaseWord(_pydantic.BaseModel):
    word_name: str 
    synonyms: str 
    antonyms: str 
    holonyms: str 
    meronyms: str 
    hyponyms: str 
    entailments: str 

class Word(_BaseWord):
    id: int 

    class Config:
        orm_mode = True

class CreateWord(_BaseWord):
    pass # pass to mean nothing extra other than base class it inherits from
