"""
/update_db.py
~~~~~~~~~~~~~

Script to update Craigslist housing and GitHub repositories database.
"""

from irahorecka import create_app
from scripts.db import update_github, update_housing, update_housing_score

application = create_app()

if __name__ == "__main__":
    update_github(application)
    update_housing(application)
    update_housing_score(application)
