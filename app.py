from flask_pymongo import PyMongo
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Online_Store"
mongo = PyMongo(app)
collection = mongo.db["animals"]

# empty array
arr = []

animaltoGet = {'commonName' : "Chipmunk"}


@app.route("/")
def index() :
    animal = collection.find_one(animaltoGet)
    print(animal)
    return render_template('index.html', animal=animal)



# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html', error=error)