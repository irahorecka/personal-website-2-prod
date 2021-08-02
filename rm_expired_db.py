"""
/rm_expired_db.py
~~~~~~~~~~~~~~~~~

Script to remove expired posts from the Craigslist housing table in database.
"""

import traceback

from irahorecka import create_app
from scripts.db import rm_expired_housing
from scripts.mail import write_email

application = create_app()

if __name__ == "__main__":
    try:
        rm_expired_housing(application)
    except Exception:
        write_email(
            "An exception occurred in 'rm_expired_db.py'",
            "An exception occurred in 'rm_expired_db.py'. Check error message below.",
            code=str(traceback.format_exc()),
        )
