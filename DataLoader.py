"""
add json files in Data/animals to mongo zoo database under animals collection
"""

from pathlib2 import Path
from pymongo import MongoClient

from util import load_json

print("Connecting to Local MongoDB")
client = MongoClient("mongodb://localhost:27017/")
db = client["zoo"]



cwd = Path.cwd()
animal_dir = cwd / 'Data' / 'animals'

files = animal_dir.glob('*.json')

# write files
for file in files:
    animal = load_json(file)
    print(f"adding {animal['CommonName']} to db")
    db.animals.insert_one(animal)



