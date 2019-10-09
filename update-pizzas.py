from pymongo import MongoClient
from bson.objectid import ObjectId
import json

client = MongoClient()
db = client.PizzaStore
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