"""
/scripts/db/setup.py
~~~~~~~~~~~~~~~~~~~~

Module for database setup.
"""

from irahorecka import db


def setup(app):
    """Sets up database models."""
    with app.app_context():
        db.create_all()
