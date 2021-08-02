"""
/irahorecka/api/craigslisthousing/read/neighborhood.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to handle the interpretation of Craigslist neighborhoods.
"""

import json
from pathlib import Path

NEIGHBORHOOD_PATH = Path(__file__).absolute().parent.joinpath("neighborhoods.json")


def read_neighborhoods():
    """Returns `neighborhoods.json` as a dictionary."""
    with open(NEIGHBORHOOD_PATH) as file:
        neighborhood = json.load(file)
    return neighborhood
