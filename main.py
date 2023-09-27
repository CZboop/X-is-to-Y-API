from fastapi import FastAPI
from x_is_to_y import XIsToYMaker
from typing import Dict

app = FastAPI(
    title = "X is to Y API",
    description = "Verbal reasoning questions finding pairs of words with the same relations",
    version = "0.1.0"
    )

question_maker = XIsToYMaker()

@app.get("/random")
def get_random_question() -> Dict:
    # TODO: have mutiple questions for multiple types of word relation, have this pick them randomly and other endpoints for each relation
    result = question_maker.create_synonym_question()
    return result

@app.get("/synonym")
def get_synonym_question() -> Dict:
    result = question_maker.create_synonym_question()
    return result

@app.get("/antonym")
def get_antonym_question() -> Dict:
    result = question_maker.create_antonym_question()
    return result