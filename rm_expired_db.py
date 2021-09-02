"""
/rm_expired_db.py
~~~~~~~~~~~~~~~~~

Script to remove expired posts from the Craigslist housing table in database.
"""

from irahorecka import create_app
from scripts.db import rm_expired_housing

application = create_app()

if __name__ == "__main__":
    # Due to Craigslist's recent policy changes, I will not remove
    # expired housing posts for archiving purposes.
    # rm_expired_housing(application)
    pass
