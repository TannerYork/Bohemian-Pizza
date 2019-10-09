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
carts = db.carts
comments = db.comments
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
    pizza_id = request.form.get('_id')
    quantity = int(request.form.get('quantity'))
    if 'anonymous-cart' in session:
        cart = session['anonymous-cart']
        if pizza_id in cart:
            for _ in range(0, quantity): cart[pizza_id] += 1
        else:
            cart.update({pizza_id: quantity})
        session['anonymous-cart'] = cart
    elif 'user' in session:
        user_id = session['user']['_id']
        cart = carts.find_one({'_id': user_id})
        if pizza_id in cart:
            carts.update_one({'_id': user_id}, {'$inc': {pizza_id: quantity}})
        else:
            carts.update_one({'_id': user_id}, {'$set': {pizza_id: quantity}})
    return redirect(url_for('pizzas_shop'))

@app.route('/update_cart', methods=['POST'])
def pizzas_update_cart():
    '''Updates selected pizzas amount in users\' cart'''
    pizza_id = request.form.get('_id')
    quantity = int(request.form.get('quantity'))
    if 'anonymous-cart' in session:
        session_cart = session['anonymous-cart']
        if quantity <= 0:
            del session_cart[pizza_id]
        else:
            pizza = { pizza_id: quantity }
            session_cart.update(pizza)
        session['anonymous-cart'] = session_cart
    elif 'user' in session:
        user_id = session['user']['_id']
        if quantity <= 0:
            carts.update_one({'_id': user_id}, {'$unset': {pizza_id: 1}})
        else:
            carts.update_one({'_id': user_id}, {'$set': {pizza_id: quantity}})
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
        session['user'] = { '_id': str(user['_id']), 'display_name': user['display_name'], 'email': user['email']}
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

@app.route('/pizzas/<pizza_id>')
def pizzas_comment(pizza_id):
    '''Renters information for a specific pizza'''
    pizza = pizzas.find_one({'_id': pizza_id})
    return render_template('pizzas_show.html', pizza=pizza)

### Helper Functions ###
def get_cart():
    '''A helper function for getting the user's cart from cookies or mongodb'''
    if 'anonymous-cart' in session:
        session_cart = session['anonymous-cart']
        cart = {}
        for key in session_cart:
            cart.update({ key: pizzas.find_one({ '_id': key }) })
            cart[key].update({ 'quantity': session_cart[key] })
        return cart
    elif 'user' in session:
        user_cart = carts.find_one({'_id': session['user']['_id']})
        if user_cart:
            cart = {}
            for key in user_cart:
                if key != '_id':
                    cart.update({ key: pizzas.find_one({ '_id': key }) })
                    cart[key].update({ 'quantity': user_cart[key] })
            return cart
        carts.insert_one({'_id': session['user']['_id']})
        return {}


if __name__ == '__main__':
    app.run(debug=True)