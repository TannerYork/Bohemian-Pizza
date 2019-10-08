from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

client = MongoClient()
db = client.PizzaStore
pizzas = db.pizzas
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/')
def pizzas_index():
    if 'anonymous-cart' not in session:
        session['anonymous-cart'] = {}
    return render_template('index.html')

@app.route('/shop')
def pizzas_shop():
    return render_template('pizzas_shop.html', pizzas=pizzas.find({}))

@app.route('/cart')
def pizzas_cart():
    cart = get_cart()
    return render_template('pizzas_cart.html', cart=cart)

@app.route('/add_pizza', methods=['POST'])
def pizzas_add():
    if 'anonymous-cart' in session:
        cart = session['anonymous-cart']
        print(cart)
        pizza_id = str(request.form.get('_id'))
        quantity = int(request.form.get('quantity'))
        if pizza_id in cart:
            for _ in range(0, quantity): cart[pizza_id] += 1
        else:
            cart.update({pizza_id: quantity})
        session['anonymous-cart'] = cart
    return redirect(url_for('pizzas_shop', pizzas=pizzas.find()))

@app.route('/update_cart', methods=['POST'])
def pizzas_update_cart():
    if 'anonymous-cart' in session:
        session_cart = session['anonymous-cart']
        if int(request.form.get('quantity')) <= 0:
            del session_cart[request.form.get('_id')]
        else:
            pizza = { request.form.get('_id'): int(request.form.get('quantity')) }
            session_cart.update(pizza)
        session['anonymous-cart'] = session_cart
        document_cart = get_cart()
    return redirect(url_for('pizzas_cart', pizzas=document_cart))

def get_cart():
    if 'anonymous-cart' in session:
        session_cart = session['anonymous-cart']
        cart = {}
        for key in session_cart:
            cart.update({ key: pizzas.find_one({ '_id': key }) })
            cart[key].update({ 'quantity': session_cart[key] })
        return cart
    else:
        return []


if __name__ == '__main__':
    app.run(debug=True)