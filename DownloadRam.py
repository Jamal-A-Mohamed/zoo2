"""
Creator: Dan Stone
Date: 4/13/2019
This script will load a list of animals from text file and download ram (or other animals)
and save the results as json and images in image dir
"""

import html2text
import os
import requests
from pathlib2 import Path
from bs4 import BeautifulSoup
import lxml
import wikipedia
from jellyfish import levenshtein_distance as dist
import re
from random import choice
import json
import urllib3


SCHEMA_FILE = Path.cwd() / 'Data' / 'animals.json'
with open(SCHEMA_FILE, 'r') as fp:
    SCHEMA = json.load(fp)

def main():

    print(Path.cwd())

    animals_file = Path.cwd() / 'Data' / 'animal_list1.txt'
    with open(animals_file, 'r') as fp:
        animals = fp.read()
        animals = animals.splitlines()

    for animal in animals:
        file = Path.cwd() / f'Data/animals/{animal}.json'
        if os.path.isfile(file): #skip downloaded already
            continue
        try:
            wiki = get_wiki_page(animal)
            if wiki:
                # print(wiki.summary)
                # print(wiki.content)
                # print(wiki.html)
                # print(wiki.title)
                # print(wiki.url)

                img_url = get_wiki_image(wiki.images, wiki.title)

                # save animal if there is image
                if img_url:
                    write_animal(file, CommonName=animal, BriefSummary=wiki.summary, WikiContents=wiki.content,
                                 ImageURL=img_url, Source=str(wiki.url))
        except Exception:
            # if some animals can not be found in wiki then we will just skip them
            pass






# img_fmt = re.compile('(.*\.jpg$)|(.*\.png$)')
# def get_wiki_image(image_urls, name) -> str:
#     '''Look through a list of image_urls and find one with closest levenshtein_distance to name
#     return url or None if no images match
#     url must match commons url (not wikipedia icons)'''
#     commons = 'https://upload.wikimedia.org/wikipedia/commons/'
#
#     # dict of url:distance
#     images = {img: (dist(name, img)-100 if name in img else dist(name, img))  for img in image_urls if commons in img and img_fmt.match(img)}
#
#     if images:
#         closest = min(images, key=images.get)
#         return str(closest)
#     else:
#         return None

def get_wiki_image(image_urls, name) -> str:
    del image_urls
    '''use wikipedia api to try to find main/primary image for page
    other pictures can often have strange things like skeletons or special features of animal'''

    url = f'https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={name}'
    try:
        response = requests.get(url)
        results = json.loads(response.text)
        # return image of first page found
        return list(results["query"]["pages"].values())[0]["original"]["source"]
    except Exception:
        print("img not found: ", url)
        return None

def get_wiki_page(name):
    try:
        wiki = wikipedia.page(name)
        return wiki
    except wikipedia.exceptions.DisambiguationError as e:
        # try to find correct page if there are multiple
        possible_entries = str(e).splitlines()
        possibles = [entry for entry in possible_entries if 'species' in entry]

        if possibles:
            return get_wiki_page(possibles[0])
    except wikipedia.exceptions.PageError:
        return None
    return None

def write_animal(file, **kwargs):
    dict_ = {k:v for k,v in kwargs.items() if k in SCHEMA.keys()} # only save elements in schema
    print(dict_)
    with open(file, 'w') as fp:
        json.dump(dict_, fp, indent=4)

if __name__ == '__main__':
    main()