from fastapi import FastAPI
from src.question_maker import QuestionMaker
from typing import Dict
import random
from contextlib import asynccontextmanager
import src.services as _services
from src.relation_writer import RelationWriter
import psycopg2
import logging
from sqlalchemy_utils.functions import database_exists, create_database

logger = logging.getLogger(__name__)
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s: %(funcName)s: %(levelname)s: %(message)s"
    )

# startup function before allowing requests, setup and populate database
@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Executes startup functionality to create and populate database if not already found, then yields the FastAPI app
    Args:
        app (FastAPI): the FastAPI app to be started up
    '''
    # checking if db exists
    logger.info("Checking for database")
    db_exists = database_exists("postgresql://postgres:password@localhost/xyapi_database")
    if not db_exists:
        logger.info("Database not found. Creating database...")
        # create fresh db to populate if not exists
        create_database('postgresql://postgres:password@localhost/xyapi_database')

        # create table based on word model
        _services._setup_tables()
        logger.info("Created table 'words' in database")
        logger.info("Populating database. This will take a few minutes...")

        # populate table with word relations
        relation_writer = RelationWriter(num_words = 100000)
        relation_writer.run("db")
        logger.info("Populated word relation database")
    else:
        logger.info("Database found")
    # yield at the end so this function only pre-startup, then main app will run
    logger.info("Starting API...")
    yield

app = FastAPI(
    title = "X is to Y API",
    description = "Verbal reasoning questions finding pairs of words with the same relations",
    version = "0.1.0",
    lifespan = lifespan,
    )

question_maker = QuestionMaker()

@app.get("/api/v1/random")
async def get_random_question() -> Dict:
    '''
    Returns a question (dict) based on random word relation.
    Return structure/types:
        {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
    '''
    question_types = ["synonyms", "antonyms", "holonyms", "meronyms", "hyponyms", "entailments",
    ]
    random_question_type = random.choice(question_types)
    result = question_maker.create_question_with_named_relation(random_question_type)
    return result

@app.get("/api/v1/synonym")
async def get_synonym_question() -> Dict:
    '''
    Returns a question (dict) based on synonym word relation.
    Return structure/types:
        {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
    '''
    result = question_maker.create_question_with_named_relation("synonyms")
    return result

@app.get("/api/v1/antonym")
async def get_antonym_question() -> Dict:
    '''
    Returns a question (dict) based on antonym word relation.
    Return structure/types:
        {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
    '''
    result = question_maker.create_question_with_named_relation("antonyms")
    return result

@app.get("/api/v1/holonym")
def get_holonym_question() -> Dict:
    '''
    Returns a question (dict) based on holonym word relation.
    Return structure/types:
        {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
    '''
    result = question_maker.create_question_with_named_relation("holonyms")
    return result

@app.get("/api/v1/meronym")
def get_meronym_question() -> Dict:
    '''
    Returns a question (dict) based on meronym word relation.
    Return structure/types:
        {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
    '''
    result = question_maker.create_question_with_named_relation("meronyms")
    return result

@app.get("/api/v1/hyponym")
def get_hyponym_question() -> Dict:
    '''
    Returns a question (dict) based on hyponym word relation.
    Return structure/types:
        {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
    '''
    result = question_maker.create_question_with_named_relation("hyponyms")
    return result

@app.get("/api/v1/entailment")
async def get_entailment_question() -> Dict:
    '''
    Returns a question (dict) based on entailment word relation.
    Return structure/types:
        {
            "first_pair": [
                str,
                str
            ],
            "second_word": str,
            "options": [
                str,
                str,
                str,
                str
            ],
            "correct_answer": str
        }
    '''
    result = question_maker.create_question_with_named_relation("entailments")
    return result