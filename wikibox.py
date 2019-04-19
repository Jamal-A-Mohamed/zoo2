"""
Author: Daniel Stone
Date: 4/13/2019
Download species taxonomical information from wikipedia infobox and add it to json
Run after DownloadRam has generated json files
"""

from pathlib2 import Path
from util import load_json, save_json
import requests
from bs4 import BeautifulSoup
import re


def main():
    cwd = Path.cwd()
    animal_dir = cwd / 'Data' / 'animals'

    files = animal_dir.glob('*.json')

    for file in files:
        animal = load_json(file)

        url = animal["Source"]

        taxonomy = get_wiki_taxonomy(url)
        if taxonomy:
            animal["Taxonomy"] = taxonomy

        save_json(animal, file)



def get_wiki_taxonomy(url):
    """look up Wikipedia url and find infobox biota and attempt to extract classification infomation
    and return it as a dictionary classification_level:classification
    e.g. {'Kingdom':'Animalia',
          'Order': "Primates'}
          """
    classifications = ['Kingdom:', 'Division:', 'Phylum:', 'Class:', 'Order:', 'Suborder:', 'Family:', 'Genus:',
                       'Species:']

    response = requests.get(url)
    soup = BeautifulSoup(response.text,'lxml')

    table = soup.find( "table", {"class":"infobox biota"})
    rows = []
    class_dict = {}
    try:
        for row in table.findAll("tr"):
            for td in row.findAll("td"):
                text = td.text.strip()
                if len(text) > 0:
                    rows.append(text)

    # find matching entries to classification entries and get next row as value

        for i in range(len(rows)-1):
            if rows[i] in classifications:
                entry = rows[i+1]
                class_dict[rows[i][:-1]] = entry
    except Exception:
        pass
    return class_dict


if __name__ == '__main__':
    main()
