import traceback

from irahorecka import create_app
from scripts.db import update_github, update_housing, update_housing_score
from scripts.mail import write_email

app = create_app()

if __name__ == "__main__":
    try:
        update_github(app)
        update_housing(app)
        update_housing_score(app)
    except Exception:
        write_email(
            "An exception occurred in 'update_db.py'",
            "An exception occurred in 'update_db.py'. Check error message below.",
            code=str(traceback.format_exc()),
        )
