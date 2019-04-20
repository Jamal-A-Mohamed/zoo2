import bcrypt as bcrypt
from flask import Flask, redirect, render_template, request, session, url_for
from flask_pymongo import PyMongo
from markdown import markdown as md
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.getcwd() + '/Static/Images'
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
        print("Logged in user: ", login_user)
        if login_user :
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == \
                    login_user['password'] :
                print(login_user['password'])
                print(bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']))
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        else :
            print("error should be printed")
            return render_template('login.html', error='<div class="alert alert-danger"> Wrong username or password<strong></strong>\
                        </div>')
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register() :
    if request.method == 'POST' :
        if (request.form['username'] == "") :
            return "username cannot be empty"
        else :
            users = mongo.db.users
            currentUser = request.form['username']
            existing_user = users.find_one({'name' : currentUser})


        if existing_user is None :
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'name' : request.form['username'], 'password' : hashpass, 'firstname' : request.form['firstname'], \
                 'lastname' : request.form['lastname']})
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
        # if session['username'] is not None:
            carenotes = None
            if "Carenotes" in animal:
                carenotes = animal["Carenotes"]
            return render_template('edit_animal.html', animal=animal, carenotes=carenotes) #username=session['username']

    update_dict = form2dict(request.form, image=request.files['image'])

    new_name = request.form.get('CommonName')
    animals.update_one({'CommonName': animal_name},
                 {"$set": update_dict})

    return redirect(f'/edit/{new_name}')


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    if request.method == 'GET':
        # if session['username'] is not None:
            return render_template('edit_animal.html', animal=None, carenotes=None) #username=session['username']
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
    care_fields = {field: form.get(field) for field in care_fields}
    update_dict = {field: form.get(field) for field in update_fields}
    update_dict["Carenotes"] = care_fields

    filename = upload_image(file=image, upload_dir=app.config['UPLOAD_FOLDER'])
    if filename:
        update_dict["ImageURL"]=filename

    return update_dict

@app.route('/logout')
def logout() :
    # remove the username from the session if it is there
    if 'username' in session :
        session.pop('username', None)
        return redirect(url_for('index'))

    else :
        return "Your are not logged in"



if __name__ == '__main__' :
    app.secret_key = 'mysecret'
    app.run(debug=True)
