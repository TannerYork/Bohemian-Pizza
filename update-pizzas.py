from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import os

db_password = os.environ.get('HEROKU_PASS')
host = os.environ.get('MONGODB_URI', f'mongodb://<bohemian-pizza-bot>:<{db_password}>@ds233288.mlab.com:33288/heroku_k546mx0r')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
pizzas = db.pizzas
pizzas.delete_many({})

pizzas_file = open('pizzas.txt', 'r')
pizza_documents = pizzas_file.readlines()
for line in pizza_documents:
    pizza_json = json.loads(line)
    name = pizza_json["name"]
    if pizza_json: pizzas.insert_one(pizza_json)
    else: print(f"Error adding {name} check for syntax error")
pizzas_file.close()