from fastapi import FastAPI
from x_is_to_y import XIsToYMaker
from typing import Dict
import random

app = FastAPI(
    title = "X is to Y API",
    description = "Verbal reasoning questions finding pairs of words with the same relations",
    version = "0.1.0"
    )

question_maker = XIsToYMaker()

@app.get("/random")
def get_random_question() -> Dict:
    # NOTE: dynamically calling method based on random choice, relies on method names being same format, could update to pick from full method name?
    question_types = ["synonym", "antonym", "hyponym", "entailment"]
    random_question_type = random.choice(question_types)
    print(random_question_type)
    result = question_maker.call_named_method(f"create_{random_question_type}_question")
    return result

@app.get("/synonym")
def get_synonym_question() -> Dict:
    result = question_maker.create_synonym_question()
    return result

@app.get("/antonym")
def get_antonym_question() -> Dict:
    result = question_maker.create_antonym_question()
    return result

@app.get("/hyponym")
def get_hyponym_question() -> Dict:
    result = question_maker.create_hyponym_question()
    return result

@app.get("/entailment")
def get_entailment_question() -> Dict:
    result = question_maker.create_entailment_question()
    return result