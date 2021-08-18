"""
/scripts/db/setup.py
~~~~~~~~~~~~~~~~~~~~

Module for database setup.
"""

from irahorecka import db
from scripts.mail import email_if_exception


@email_if_exception
def setup(app):
    """Sets up database models."""
    with app.app_context():
        db.create_all()
