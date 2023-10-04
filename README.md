# X is to Y API 🕸️
Python REST API serving "X is to Y" style verbal reasoning questions, made with FastAPI, the NLTK interface for WordNet and a PostgreSQL database.

Below is an example of the type of question the API is intended to help create:

> Run is to sprint as talk is to: 
> - A. Walk
> - B. Shout
> - C. Type
> - D. Draw

## Endpoints
All of the endpoints use GET requests and do not take in any information, either in the request body or as query string.

`GET` **`/api/v1/random`**
- Returns an object with answers and options for two sets of words with the same relation, but the type of relation is random

`GET` **`/api/v1/synonym`**
- Returns an object with answers and options for two sets of words with a synonym relation

`GET` **`/api/v1/antonym`** 
- Returns an object with answers and options for two sets of words with an antonym relation

`GET` **`/api/v1/holonym`**
- Returns an object with answers and options for two sets of words with a holonym relation

`GET` **`/api/v1/meronym`**
- Returns an object with answers and options for two sets of words with a meronym relation

`GET` **`/api/v1/hyponym`**
- Returns an object with answers and options for two sets of words with the a hyponym relation

`GET` **`/api/v1/entailment`**
- Returns an object with answers and options for two sets of words with an entailment relation

### Example response
All endpoints return the same format of response if successful.
This is an example of the response:

```json
{
    "first_pair": [
        "cowardly",
        "brave"
    ],
    "second_word": "appreciated",
    "options": [
        "regarded",
        "depreciate",
        "limpidly",
        "tomatillo"
    ],
    "correct_answer": "depreciate"
}
```
