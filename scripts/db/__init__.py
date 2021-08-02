"""
/scripts/db/__init__.py

Concerns all things database write and update.
"""

from functools import partial

from irahorecka import create_app
from scripts.db.setup import setup
from scripts.db.update import update_github, update_housing, update_housing_score, rm_expired_housing
