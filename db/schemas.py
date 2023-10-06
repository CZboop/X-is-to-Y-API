import pydantic as _pydantic

class _BaseWord(_pydantic.BaseModel):
    '''
    Defines the data types for the user defined attributes of a word (all but id) as a pydantic model
    '''
    word_name: str 
    synonyms: str 
    antonyms: str 
    holonyms: str 
    meronyms: str 
    hyponyms: str 
    entailments: str 

class Word(_BaseWord):
    '''
    Constructor for creating a word object to be added to a SQL database from args
    Args:
        word_name (str): The word itself
        synonyms (str): Synonyms of the word (1 or more words separated by spaces)
        antonyms (str): Antonyms of the word (1 or more words separated by spaces)
        holonyms (str): Holonyms of the word (1 or more words separated by spaces)
        meronyms (str): Meronyms of the word (1 or more words separated by spaces)
        hyponyms (str): Hyponyms of the word (1 or more words separated by spaces)
        entailments (str): Entailments of the word (1 or more words separated by spaces)
    Constructs word object with these properties plus an id (int)
    '''
    id: int 

    class Config:
        from_attributes = True

class CreateWord(_BaseWord):
    '''
    More user-friendlily name constructor for creating a word object to be added to a SQL database from args
    Args:
        word_name (str): The word itself
        synonyms (str): Synonyms of the word (1 or more words separated by spaces)
        antonyms (str): Antonyms of the word (1 or more words separated by spaces)
        holonyms (str): Holonyms of the word (1 or more words separated by spaces)
        meronyms (str): Meronyms of the word (1 or more words separated by spaces)
        hyponyms (str): Hyponyms of the word (1 or more words separated by spaces)
        entailments (str): Entailments of the word (1 or more words separated by spaces)
    Constructs word object with these properties plus an id (int)
    '''
    pass
