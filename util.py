"""
Author: Daniel Stone
Date: 4/13/2019

Some utility functions for this project
"""

import json
import os
from pathlib2 import Path
from PIL import Image
import PIL


def load_json(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def save_json(obj, path, indent=4):
    path = Path(path)
    os.makedirs(path.parent, exist_ok='True')
    with open(path, 'w') as fp:
        json.dump(obj, fp, indent=indent)


def resize_image(fp, width_target=480, file_out=None):
    try:
        fp = str(fp)
        img = Image.open(fp)
        width, height = img.size

        height_target = int((float(height) * float(width_target / width)))
        img = img.resize((width_target, height_target), PIL.Image.ANTIALIAS)

        # if output not specified save to original path
        if file_out is None:
            file_out = fp
        else:
            file_out=str(file_out)
        img.save(file_out)
    except Exception as e:
        print(e)


