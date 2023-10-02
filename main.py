from fastapi import FastAPI
from question_maker import QuestionMaker
from typing import Dict
import random

app = FastAPI(
    title = "X is to Y API",
    description = "Verbal reasoning questions finding pairs of words with the same relations",
    version = "0.1.0"
    )

question_maker = QuestionMaker()

@app.get("/api/v1/random")
async def get_random_question() -> Dict:
    # NOTE: dynamically calling method based on random choice, relies on method names being same format
    question_types = ["synonym", "antonym", "holonym", "meronym", "hyponym", "entailment",
    # 
    ]
    random_question_type = random.choice(question_types)
    print(random_question_type)
    result = question_maker.call_named_method(f"create_{random_question_type}_question")
    return result

@app.get("/api/v1/synonym")
async def get_synonym_question() -> Dict:
    result = question_maker.create_synonym_question()
    return result

@app.get("/api/v1/antonym")
async def get_antonym_question() -> Dict:
    result = question_maker.create_antonym_question()
    return result

@app.get("/api/v1/holonym")
def get_holonym_question() -> Dict:
    result = question_maker.create_holonym_question()
    return result

@app.get("/api/v1/meronym")
def get_meronym_question() -> Dict:
    result = question_maker.create_meronym_question()
    return result

@app.get("/api/v1/hyponym")
def get_hyponym_question() -> Dict:
    result = question_maker.create_hyponym_question()
    return result

@app.get("/api/v1/entailment")
async def get_entailment_question() -> Dict:
    result = question_maker.create_entailment_question()
    return result