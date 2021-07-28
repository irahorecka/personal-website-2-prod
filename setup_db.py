import os
import traceback

from irahorecka import create_app
from scripts.db import setup
from scripts.mail import write_email

app = create_app()

if __name__ == "__main__":
    # Validate environment variable keys
    env_vars = ["EMAIL_USER", "EMAIL_PASS", "SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "GITHUB_TOKEN"]
    for var in env_vars:
        os.environ[var]
    try:
        setup(app)
    except Exception:
        write_email(
            "An exception occurred in 'setup_db.py'",
            "An exception occurred during database setup in 'setup_db.py'. Check error message below.",
            code=str(traceback.format_exc()),
        )
