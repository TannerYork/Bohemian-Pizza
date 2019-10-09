from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime
import os

client = MongoClient()
db = client.PizzaStore
pizzas = db.pizzas
users = db.users
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/')
def pizzas_index():
    '''Renders the landing page'''
    if 'user' in session:
        return render_template('index.html', user=session['user'])
    elif 'anonymous-cart' not in session:
        session['anonymous-cart'] = {}
    return render_template('index.html')

@app.route('/shop')
def pizzas_shop():
    '''Renders the shop page with avalable pizzas from mongodb database'''
    return render_template('pizzas_shop.html', pizzas=pizzas.find({}))

@app.route('/cart')
def pizzas_cart():
    '''Renders the users cart which contains the users selected pizzas and the quantity of each'''
    cart = get_cart()
    return render_template('pizzas_cart.html', cart=cart)

@app.route('/add_pizza', methods=['POST'])
def pizzas_add():
    '''Uploads pizzas\' _id to users cart'''
    if 'anonymous-cart' in session:
        cart = session['anonymous-cart']
        pizza_id = str(request.form.get('_id'))
        quantity = int(request.form.get('quantity'))
        if pizza_id in cart:
            for _ in range(0, quantity): cart[pizza_id] += 1
        else:
            cart.update({pizza_id: quantity})
        session['anonymous-cart'] = cart
    return redirect(url_for('pizzas_shop'))

@app.route('/update_cart', methods=['POST'])
def pizzas_update_cart():
    '''Updates selected pizzas amount in users\' cart'''
    if 'anonymous-cart' in session:
        session_cart = session['anonymous-cart']
        if int(request.form.get('quantity')) <= 0:
            del session_cart[request.form.get('_id')]
        else:
            pizza = { request.form.get('_id'): int(request.form.get('quantity')) }
            session_cart.update(pizza)
        session['anonymous-cart'] = session_cart
    return redirect(url_for('pizzas_cart'))

@app.route('/login')
def pizzas_login():
    '''Render the login page'''
    if 'user' in session: return render_template('pizzas_login.html', user=True)
    else: return render_template('pizzas_login.html')
    
@app.route('/user-login', methods=["POST"])
def user_login():
    '''Login user if password is correct'''
    user = users.find_one({'email': request.form.get('email')})
    encoded_pass = request.form.get('password').encode('utf-8')
    if user and bcrypt.checkpw(encoded_pass, user['password']):
        session.clear()
        session['user'] = { 'display_name': user['display_name'], 'email': user['email']}
        return redirect(url_for('pizzas_index'))
    return render_template('pizzas_login.html', error=True)

@app.route('/user-logout', methods=["POST"])
def user_logout():
    '''Logout user'''
    if 'user' in session: del session['user']
    return redirect(url_for('pizzas_index'))
    
@app.route('/registure')
def pizzas_registure():
    if 'user' in session: return render_template('pizzas_registure.html', user=True)
    else: return render_template('pizzas_registure.html')

@app.route('/user-registure', methods=["POST"])
def user_registure():
    '''Add a new user to mongodb database'''
    encoded_pass = request.form.get('password').encode('utf-8')
    user = {
        'display_name': request.form.get('display_name'),
        'email': request.form.get('email'),
        'password': bcrypt.hashpw(encoded_pass, bcrypt.gensalt())
    }
    user_exist = users.find_one({'email': user['email']})
    if user_exist:
        return render_template('pizzas_registure.html', user_exist=True)
    else:
        users.insert_one(user)
        return redirect(url_for('pizzas_login'))

def get_cart():
    '''A helper function for getting the user's cart from cookies or mongodb'''
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