from functools import partial

from irahorecka import create_app
from scripts.db.setup import setup
from scripts.db.update import update_github, update_housing, update_housing_score
