"""
/setup_db.py
~~~~~~~~~~~~

Script to check for correctly configured environment variables and set up database.
"""

import os

from dotenv import load_dotenv

from irahorecka import create_app
from scripts.db import setup

load_dotenv()
application = create_app()

if __name__ == "__main__":
    # Validate environment variable keys.
    env_vars = ["EMAIL_USER", "EMAIL_PASS", "SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "GITHUB_TOKEN"]
    for var in env_vars:
        # Unprotected key calls - trigger exception if key doesn't exist.
        os.environ[var]
    setup(application)
