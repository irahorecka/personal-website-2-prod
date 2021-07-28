import traceback

from irahorecka import create_app
from scripts.db import update_github, update_housing, update_housing_score
from scripts.mail import write_email

application = create_app()

if __name__ == "__main__":
    try:
        update_github(application)
        update_housing(application)
        update_housing_score(application)
    except Exception:
        write_email(
            "An exception occurred in 'update_db.py'",
            "An exception occurred in 'update_db.py'. Check error message below.",
            code=str(traceback.format_exc()),
        )
