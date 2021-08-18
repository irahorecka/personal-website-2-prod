"""
/rm_expired_db.py
~~~~~~~~~~~~~~~~~

Script to remove expired posts from the Craigslist housing table in database.
"""

from irahorecka import create_app
from scripts.db import rm_expired_housing

application = create_app()

if __name__ == "__main__":
    rm_expired_housing(application)
