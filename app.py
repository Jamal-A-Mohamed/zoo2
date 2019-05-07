#!/usr/bin/python3

import os
import re
from functools import wraps
from random import choice

import bcrypt
from bleach import clean
from flask import Flask, redirect, render_template, request, session, url_for, abort, Response, json, make_response
from flask_pymongo import PyMongo
from markdown import markdown
from werkzeug.utils import secure_filename

from util import random_banner

# regex for heading substitution (BriefSummary => Brief Summary)
camel_re = re.compile(r'(?!^)(?=[A-Z])')




UPLOAD_FOLDER = os.getcwd() + '/Static/Images'
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')

SESSION_COOKIE_SECURE = True

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MONGO_URI"] = "mongodb://localhost:27017/zoo"
app.secret_key = 'mysecret'
mongo = PyMongo(app)
collection = mongo.db["animals"]


static_site = "https://ninth.site"


# empty array
arr = []

animaltoGet = {'CommonName': "Addax"}
animal_list = list(sorted([animal['CommonName'] for animal in collection.find({})]))


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def noindex(f):
    """This decorator passes X-Robots-Tag: noindex"""
    @wraps(f)
    @add_response_headers({'X-Robots-Tag': 'noindex'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def XXSSP(f):
    """This decorator passes X-XSS-Protection: 1"""
    @wraps(f)
    @add_response_headers({'X-XSS-Protection': 1})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def HSTS(f):
    """This decorator passes X-XSS-Protection: 1"""
    @wraps(f)
    @add_response_headers({'Strict-Transport-Security': "max-age=31536000; includeSubdomains;"})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def secure_headers(f):
    """This decorator passes X-XSS-Protection: 1"""
    @wraps(f)
    @add_response_headers({'X-XSS-Protection': 1})
    @add_response_headers({'X-Content-Type-Options': "nosniff"})
    @add_response_headers({'X-Frame-Options': "deny"})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

@app.route("/Static/{etc}")
def static123(etc):
    return redirect(f"{static_site}/Static/{etc}")


@app.route("/")
@secure_headers
@HSTS
def index():
    animal = collection.find_one({'CommonName': choice(animal_list)})
    animal2 = collection.find_one({'CommonName': choice(animal_list)})
    animal3 = collection.find_one({'CommonName': choice(animal_list)})
    animal['html_summary'] = md(animal['BriefSummary'])
    animal2['html_summary'] = md(animal2['BriefSummary'])
    animal3['html_summary'] = md(animal3['BriefSummary'])

    return render_template('index.html', static_site=static_site, animal=animal, animal2=animal2, animal3=animal3, banner=random_banner())


@app.route("/glossary")
@secure_headers
@HSTS
def glossary():
    return render_template('glossary.html', animal_list=animal_list, category="animals", static_site=static_site)


@app.route("/reptiles")
@secure_headers
@HSTS
def reptiles():
    reptile_list = get_animals_from_classification(level="Class", classification="Reptilia")
    return render_template('glossary.html', animal_list=reptile_list, category="reptiles", static_site=static_site)

@app.route("/birds")
@secure_headers
@HSTS
def theword():
    bird_list = get_animals_from_classification(level="Class", classification="Aves")
    return render_template('glossary.html', animal_list=bird_list, category="birds", static_site=static_site)

@app.route("/mammals")
@secure_headers
@HSTS
def mammals():
    mammal_list = get_animals_from_classification(level="Phylum", classification="Chordata")
    return render_template('glossary.html', animal_list=mammal_list, category="mammals", static_site=static_site)


@app.route("/results/<name_searched>")
@secure_headers
@HSTS
def search_results(name_searched):
    print(name_searched)
    results_list = [animal['CommonName'] for animal in collection.find({"CommonName":{"$regex": f'.*({name_searched}).*'}})]
    results_list += [animal['CommonName'] for animal in collection.find({"ScientificName":{"$regex": f'.*({name_searched}).*'}})]
    print(results_list)
    results_list = list(sorted(set(results_list)))
    return render_template('glossary.html', animal_list=results_list, category="Search Results", static_site=static_site)



@app.route("/results/<name_searched>")
@secure_headers
@HSTS
def search_results(name_searched):
    print(name_searched)
    results_list = [animal['CommonName'] for animal in collection.find({"CommonName":{"$regex": f'.*({name_searched}).*'}})]
    results_list += [animal['CommonName'] for animal in collection.find({"ScientificName":{"$regex": f'.*({name_searched}).*'}})]
    print(results_list)
    results_list = list(sorted(set(results_list)))
    return render_template('glossary.html', animal_list=results_list, category="Search Results")


@app.route('/search', methods=['POST', 'GET'])
@secure_headers
@HSTS
def search():
    if request.method == 'POST':
        entry = request.form['animalname']
        if entry in animal_list:
            return redirect(url_for('animal_page', animal_name=entry))
        else:
            return redirect(url_for('search_results', name_searched=entry))


@app.route('/autocomplete', methods=['GET'])
def autocomplete() :
    search = request.args.get('animalname')

    app.logger.debug(search)
    print(search)

    return Response(json.dumps(animal_list), mimetype='application/json')


@app.route('/random/')
@app.route('/random')
def random_animal():
    rand_animal = choice(animal_list)
    print(rand_animal)
    return redirect(url_for('animal_page', animal_name=f"{rand_animal}"))


@app.route('/animal/<animal_name>')
@secure_headers
@HSTS
def animal_page(animal_name):
    if animal_name is None:
        abort(404)
    animal = collection.find_one_or_404({"CommonName": animal_name})

    convert_md = ('BriefSummary', 'FunFacts', "Diet", "Habitat", "Zone")

    for field in convert_md:
        if field in animal:
            animal[field] = md(animal[field], field)

    if "Source" in animal:
        animal["attribution"] = wiki_attribution(animal["Source"])

    carenotes = None
    if "Carenotes" in animal:
        carenotes = animal["Carenotes"]
        for field in carenotes.keys():
            carenotes[field] = md(carenotes[field], field, heading='h4')
    return render_template('animal.html', static_site=static_site, animal=animal, carenotes=carenotes)


@app.route('/login', methods=['POST', 'GET'])
@secure_headers
@HSTS
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
            return render_template('login.html', static_site=static_site, error='<div class="alert alert-danger"> Wrong username or password<strong></strong>\
                        </div>')
    return render_template('login.html', static_site=static_site)


@app.route('/logout')
@secure_headers
@HSTS
def logout():
    # remove the username from the session if it is there
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('index'))
    else :
        return "Your are not logged in,You don't need to log off"


@app.route('/register', methods=['POST', 'GET'])
@secure_headers
@HSTS
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
                {'name' : request.form['username'], 'password' : hashpass, 'firstname' : request.form['firstname'],
                 'lastname': request.form['lastname']})
            session['username'] = request.form['username']

            return redirect(url_for('index'))

        return render_template('register.html', error='<div class="alert alert-danger"> Username Already exists<strong></strong>\
                        </div>')

    return render_template('register.html', static_site=static_site)


@app.route('/edit/<animal_name>', methods=['POST', 'GET'])
@secure_headers
@HSTS
def edit_animal(animal_name):
    animals = mongo.db.animals
    animal = animals.find_one({'CommonName': animal_name})

    if request.method == 'GET':
        if 'username' in session:
            # if session['username'] is not None:
            carenotes = None
            if "Carenotes" in animal:
                carenotes = animal["Carenotes"]
            return render_template('edit_animal.html', static_site=static_site, animal=animal,
                                   carenotes=carenotes)  # username=session['username']
        else:
            return "You are not logged in"

    update_dict = form2dict(request.form, image=request.files['image'])

    new_name = request.form.get('CommonName')
    animals.update_one({'CommonName': animal_name},
                       {"$set": update_dict})

    return redirect(f'/edit/{new_name}')


@app.route('/edit', methods=['POST', 'GET'])
@secure_headers
@HSTS
def edit():
    if request.method == 'GET':
        # if session['username'] is not None:
        return render_template('edit_animal.html',static_site=static_site, animal=None, carenotes=None)  # username=session['username']
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
    update_fields = ["ScientificName", "BriefSummary", "FunFacts", "Diet", "Habitat", "Zone"] + ["CommonName"] * addName
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
        return f'<{heading}>{str(camel_re.sub(" ", header))}</{heading}>' + markdown(clean(text))
    return markdown(clean(text))

def get_animals_from_classification(level, classification):

    key = f"Taxonomy.{level}"
    value = classification
    matching = [animal['CommonName'] for animal in collection.find({key:value})]
    return list(sorted(matching))


def wiki_attribution(source_url):
    return f'This article uses material from the Wikipedia article <a href="{source_url}">"{source_url.split("/")[-1]}"</a>, which is released under the <a href="https://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-Share-Alike License 3.0</a> '

if __name__ == '__main__':
    app.secret_key = 'JR4WRBQUR6SDKuPTjrkCGBJ2UFF2TXxqhh'
    app.run(ssl_context=('fullchain.pem','privkey.pem'), host="0.0.0.0", port=5002)
    # app.run(ssl_context=('fullchain.pem','privkey.pem'))


