from fastapi import FastAPI
from x_is_to_y import XIsToYMaker

app = FastAPI()

question_maker = XIsToYMaker()

@app.get("/random")
def get_random_question() -> str:
    result = question_maker.create_synonym_question()
    return result