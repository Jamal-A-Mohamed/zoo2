"""
add json files in Data/animals to mongo zoo database under animals collection
"""

from pymongo import MongoClient
from pathlib2 import Path
from util import load_json

print("Connecting to Local MongoDB")
client = MongoClient("mongodb://localhost:27017/")
db = client["zoo"]

# animal = {'Imageurl':"https://en.wikipedia.org/wiki/File:Chipmunk_(71669).jpg","ScientificName":"Marmotini",'Briefsummary':"Chipmunks are small, striped rodents of the family Sciuridae. Chipmunks are found in North America, with the exception of the Siberian chipmunk which is found primarily in Asia",'commonName':"Chipmunk"}


cwd = Path.cwd()
animal_dir = cwd / 'Data' / 'animals'

files = animal_dir.glob('*.json')

# write files
for file in files:
    animal = load_json(file)
    print(f"adding {animal['CommonName']} to db")
    db.animals.insert_one(animal)



