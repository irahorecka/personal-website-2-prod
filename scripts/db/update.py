"""
/scripts/db/update.py
~~~~~~~~~~~~~~~~~~~~~

Module for database updates.
"""

import irahorecka.api as api
from scripts.mail import email_if_exception


@email_if_exception
def update_github(app):
    """Updates database with GitHub repository information."""
    with app.app_context():
        api.write_github_repos()


@email_if_exception
def update_housing(app):
    """Update database with Craigslist housing information."""
    with app.app_context():
        # The following calls must go in this order.
        api.write_craigslist_housing(site="sfbay", areas=["eby", "nby", "sby", "sfc", "pen", "scz"])
        api.clean_craigslist_housing()


@email_if_exception
def update_housing_score(app):
    """Updates Craigslist housing table with post scores."""
    with app.app_context():
        api.write_craigslist_housing_score(site="sfbay", areas=["eby", "nby", "sby", "sfc", "pen", "scz"])


@email_if_exception
def rm_expired_housing(app):
    """Removes expired Craigslist housing posts from table in database."""
    with app.app_context():
        api.rm_expired_craigslist_housing()
