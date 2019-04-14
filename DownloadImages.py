"""
Author: Daniel Stone
Date: 4/13/2019
Download wiki images and save them to Image folder and change .json data file to new image name
"""

from pathlib2 import Path
from util import load_json, save_json
import requests
import shutil
import mimetypes


def main():
    cwd = Path.cwd()
    animal_dir = cwd / 'Data' / 'animals'

    files = animal_dir.glob('*.json')

    for file in files:
        animal = load_json(file)

        url = animal["ImageURL"]

        img_path = cwd / 'Images' / file.stem

        image_loc = download_image(url, img_path)

        animal["ImageURL"] = Path(image_loc).name

        save_json(animal, file)




def download_image(url, save_file):
    response = requests.get(url, stream=True)
    extension = get_extension(url)
    if extension is None:
        # try to find extension from response headers
        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type)

    # save to file with extension found
    output_file = save_file.parent / (letters(str(save_file.stem))+extension) #quickfix remove non a-z_ characters from images
    with open(output_file, 'wb') as fp:
        shutil.copyfileobj(response.raw, fp)
    return output_file


def get_extension(url):
    """Try to find known image file extension in url"""
    img_extensions = ('.jpg', '.png', '.jpeg', '.svg', '.gif', '.tiff', '.xcf')
    for ext in img_extensions:
        if ext in url:
            return ext
    return None

def letters(input):
    return ''.join(c for c in input if c.isalpha())

if __name__ == '__main__':
    main()