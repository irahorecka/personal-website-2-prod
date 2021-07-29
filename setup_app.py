import os
import traceback

from irahorecka import create_app
from scripts.db import setup
from scripts.mail import write_email

application = create_app()

if __name__ == "__main__":
    # Validate environment variable keys
    env_vars = ["EMAIL_USER", "EMAIL_PASS", "SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "GITHUB_TOKEN"]
    for var in env_vars:
        # Unprotected key calls - trigger exception if key doesn't exist
        os.environ[var]
    try:
        setup(application)
    except Exception:
        write_email(
            "An exception occurred in 'setup_app.py'",
            "An exception occurred during database setup in 'setup_app.py'. Check error message below.",
            code=str(traceback.format_exc()),
        )
    # Success
    write_email(
        "Python script 'setup_app.py' completed successfully.",
        "Python script 'setup_app.py' completed successfully. Please proceed with updating the database with CraigslistHousing and GitHub repo contents.",
    )
