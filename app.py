import bcrypt as bcrypt
from flask import Flask, redirect, render_template, request, session, url_for
from flask_pymongo import PyMongo
from markdown import markdown as md

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/zoo"
app.secret_key = 'mysecret'
mongo = PyMongo(app)
collection = mongo.db["animals"]

# empty array
arr = []

animaltoGet = {'CommonName' : "Addax"}



@app.route("/")
def index() :
    animal = collection.find_one(animaltoGet)
    print(animal)
    animal['html_summary'] = md(animal['BriefSummary'])
    print(animal)

    return render_template('index.html', animal=animal)


# # Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             return redirect(url_for('index'))
#     return render_template('login.html')


# app.config['DEBUG'] = True


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' :
        users = mongo.db.users
        login_user = users.find_one({'name' : request.form['username']})

        if login_user :
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == \
                    login_user['password'] :
                print(login_user['password'])
                print(bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']))
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        return render_template('login.html', error="Wrong password or username")
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register() :
    if request.method == 'POST' :
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None :
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']

            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


if __name__ == '__main__' :
    app.secret_key = 'mysecret'
    app.run(debug=True)
