from pymongo import MongoClient


print("Connecting to Local MongoDB")
client = MongoClient("mongodb://localhost:27017/") #connecting to database

print("Connecting to Online_Store")
online_store = client["Online_Store"]

#create a document in CS485
print("creating a document on Online_Store")
animal = {'Imageurl':"https://en.wikipedia.org/wiki/File:Chipmunk_(71669).jpg","ScientificName":"Marmotini",'Briefsummary':"Chipmunks are small, striped rodents of the family Sciuridae. Chipmunks are found in North America, with the exception of the Siberian chipmunk which is found primarily in Asia",'commonName':"Chipmunk"}

    #insert document in database
online_store.animals.insert_one(animal)


