from flask_pymongo import PyMongo
from flask import Flask, render_template

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Online_Store"
mongo = PyMongo(app)
collection = mongo.db["animals"]

# empty array
arr = []

animaltoGet = {'commonName' : "Chipmunk"}


@app.route("/")
def home_page():
    animal = collection.find_one(animaltoGet)
    print(animal)
    return render_template('index.html', animal=animal)


