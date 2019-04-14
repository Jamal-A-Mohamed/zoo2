"""
Author: Daniel Stone
Date: 4/13/2019

Some utility functions for this project
"""

import json
import os
from pathlib2 import Path


def load_json(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def save_json(obj, path, indent=4):
    path = Path(path)
    os.makedirs(path.parent, exist_ok='True')
    with open(path, 'w') as fp:
        json.dump(obj, fp, indent=indent)
