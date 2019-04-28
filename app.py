#!/usr/bin/python3

import bcrypt
import os
from random import choice
from flask import Flask, redirect, render_template, request, session, url_for, abort, Response, json
from flask_pymongo import PyMongo
from markdown import markdown
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.getcwd() + '/Static/Images'
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MONGO_URI"] = "mongodb://localhost:27017/zoo"
app.secret_key = 'mysecret'
mongo = PyMongo(app)
collection = mongo.db["animals"]
from util import random_banner

# empty array
arr = []

animaltoGet = {'CommonName': "Addax"}
animal_list = [animal['CommonName'] for animal in collection.find({})]


@app.route("/")
def index():
    animal = collection.find_one({'CommonName': choice(animal_list)})
    animal2 = collection.find_one({'CommonName': choice(animal_list)})
    animal3 = collection.find_one({'CommonName': choice(animal_list)})
    animal['html_summary'] = md(animal['BriefSummary'])
    animal2['html_summary'] = md(animal2['BriefSummary'])
    animal3['html_summary'] = md(animal3['BriefSummary'])

    return render_template('index.html', animal=animal, animal2=animal2, animal3=animal3, banner=random_banner())


@app.route("/glossary")
def glossary():
    return render_template('glossary.html', animal_list=animal_list)



@app.route("/autocomplete")
def autcomplete() :
    return render_template('autocomplete.html', animal_list=animal_list)

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        return redirect(url_for('animal_page', animal_name=request.form['animalname']))

#
# @app.route('/autocomplete', methods=['GET'])
# def autocomplete() :
#     search = request.args.get('q')
#     print(search)
#
#     if search and len(search) >= 3:
#         results = [animal for animal in animal_list if search in animal]
#         print(results)
#         return jsonify(matching_results=results)
#     return "NOTHING IN THE SEARCH BAR"



@app.route('/animalname', methods=['GET'])
def autocomplete() :
    search = request.args.get('animalname')

    app.logger.debug(search)
    print(search)

    print(Response(json.dumps(NAMES)))
    return Response(json.dumps(animal_list), mimetype='application/json')


@app.route('/random/')
@app.route('/random')
def random_animal():
    rand_animal = choice(animal_list)
    print(rand_animal)
    return redirect(url_for('animal_page', animal_name=f"{rand_animal}"))


@app.route('/animal/<animal_name>')
def animal_page(animal_name):
    if animal_name is None:
        abort(404)
    animal = collection.find_one_or_404({"CommonName": animal_name})

    convert_md = ('BriefSummary', 'FunFacts', "Diet", "Habitat")

    for field in convert_md:
        if field in animal:
            animal[field] = md(animal[field], field)

    carenotes = None
    if "Carenotes" in animal:
        carenotes = animal["Carenotes"]
        for field in carenotes.keys():
            carenotes[field] = md(carenotes[field], field, heading='h4')
    return render_template('animal.html', animal=animal, carenotes=carenotes)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return "User already logged in"

    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': request.form['username']})
        print("Logged in user: ", login_user)
        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == \
                    login_user['password']:
                print(login_user['password'])
                print(bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']))
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        else:
            print("error should be printed")
            return render_template('login.html', error='<div class="alert alert-danger"> Wrong username or password<strong></strong>\
                        </div>')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('index'))
    else :
        return "Your are not logged in,You don't need to log off"


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if (request.form['username'] == ""):
            return "username cannot be empty"
        else:
            users = mongo.db.users
            currentUser = request.form['username']
            existing_user = users.find_one({'name': currentUser})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'name': request.form['username'], 'password': hashpass, 'firstname': request.form['firstname'], \
                 'lastname': request.form['lastname']})
            session['username'] = request.form['username']

            return redirect(url_for('index'))

        return render_template('register.html', error='<div class="alert alert-danger"> Username Already exists<strong></strong>\
                        </div>')

    return render_template('register.html')


@app.route('/edit/<animal_name>', methods=['POST', 'GET'])
def edit_animal(animal_name):
    animals = mongo.db.animals
    animal = animals.find_one({'CommonName': animal_name})

    if request.method == 'GET':
        if 'username' in session:
            # if session['username'] is not None:
            carenotes = None
            if "Carenotes" in animal:
                carenotes = animal["Carenotes"]
            return render_template('edit_animal.html', animal=animal,
                                   carenotes=carenotes)  # username=session['username']
        else:
            return "You are not logged in"

    update_dict = form2dict(request.form, image=request.files['image'])

    new_name = request.form.get('CommonName')
    animals.update_one({'CommonName': animal_name},
                       {"$set": update_dict})

    return redirect(f'/edit/{new_name}')


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    if request.method == 'GET':
        # if session['username'] is not None:
        return render_template('edit_animal.html', animal=None, carenotes=None)  # username=session['username']
    animals = mongo.db.animals

    update_dict = form2dict(request.form, image=request.files['image'])
    # TODO: make sure animal not already in system

    animals.insert_one(update_dict)

    return redirect(url_for('edit'))


def upload_image(file, upload_dir):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_dir, filename))
        print("File was uploaded:", filename)
        return filename
    return None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def form2dict(form, image=None, addName=True):
    """return elements to update from form as a dict for update or insert to mongo"""
    update_fields = ["ScientificName", "BriefSummary", "FunFacts", "Diet", "Habitat"] + ["CommonName"] * addName
    care_fields = ["FeedingSchedule", "Food", "Notes"]
    care_fields = {field: form.get(field) for field in care_fields if len(form.get(field)) > 0}
    update_dict = {field: form.get(field) for field in update_fields if len(form.get(field)) > 0}
    update_dict["Carenotes"] = care_fields

    filename = upload_image(file=image, upload_dir=app.config['UPLOAD_FOLDER'])
    if filename:
        update_dict["ImageURL"] = filename

    return update_dict



def md(text, header=None, heading='h2'):
    if header and heading in ('h1', 'h2', 'h3', 'h4'):
        return f'<{heading}>{header}</{heading}>' + markdown(text)
    return markdown(text)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host="0.0.0.0", port=5002)
    # app.run(host="127.0.0.1", port=5000)

