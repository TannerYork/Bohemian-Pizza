from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

client = MongoClient()
db = client.PizzaStore
pizzas = db.pizzas
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def pizzas_shop():
    return render_template('pizzas_shop.html', pizzas=pizzas.find())

if __name__ == '__main__':
    app.run()