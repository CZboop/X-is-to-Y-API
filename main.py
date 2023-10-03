from fastapi import FastAPI
from question_maker import QuestionMaker
from typing import Dict
import random
from contextlib import asynccontextmanager
import services as _services
from relation_writer import RelationWriter
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