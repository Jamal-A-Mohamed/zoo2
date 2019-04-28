"""
Author: Daniel Stone
Date: 4/13/2019
Verify that animals has Taxonomy info and Image

If not delete the json files and images
"""

from pathlib2 import Path
from util import load_json
import os


def main():
    cwd = Path.cwd()
    animal_dir = cwd / 'Data' / 'animals'

    files = animal_dir.glob('*.json')
    animals_found = []
    for file in files:
        animal = load_json(file)

        url = animal["Source"]

        if ("Taxonomy" not in animal or "ImageURL" not in animal) or \
                "ImageURL" in animal and "_sm" not in animal["ImageURL"] or \
                animal["CommonName"] in animals_found:
            # print(animal["CommonName"], "Taxonomy" in animal, "ImageURL" in animal)
            # print(animal["ImageURL"])

            print(file)
            image_file = cwd / 'Static'/'Images'/animal["ImageURL"]
            print(image_file)
            os.remove(file)
            os.remove(image_file)

        animals_found.append(animal["CommonName"])

    print(sorted(list(animals_found)))
    print(len(set(animals_found)))
if __name__ == '__main__':
    main()
