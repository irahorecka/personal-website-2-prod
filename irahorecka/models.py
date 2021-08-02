"""
/irahorecka/models.py
~~~~~~~~~~~~~~~~~~~~~

Module to store database models used in the Flask application.
"""

from irahorecka import db


class GitHubRepo(db.Model):
    """Model for a GitHub repository."""

    __tablename__ = "githubrepo"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    full_name = db.Column(db.String(120))
    description = db.Column(db.String(240))
    license = db.Column(db.String(80))
    private = db.Column(db.String(20))
    stars = db.Column(db.Integer)
    forks = db.Column(db.Integer)
    commits = db.Column(db.Integer)
    open_issues = db.Column(db.Integer)
    languages = db.relationship("RepoLanguage", backref="repo")
    url = db.Column(db.String(240))

    def __repr__(self):
        return f"GitHubRepo(name={self.name})"


class RepoLanguage(db.Model):
    """Model for a GitHub repository's language(s)."""

    __tablename__ = "repolanguage"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    color = db.Column(db.String(20))
    repo_id = db.Column(db.Integer, db.ForeignKey("githubrepo.id"))

    def __repr__(self):
        return f"RepoLanguage(name={self.name})"


class CraigslistHousing(db.Model):
    """Model for Craigslist housing post attributes."""

    __tablename__ = "craigslisthousing"
    # `id` is the Craigslist's post ID
    id = db.Column(db.BigInteger, primary_key=True)
    site = db.Column(db.String(8))
    area = db.Column(db.String(8))
    repost_of = db.Column(db.String(20))
    last_updated = db.Column(db.DateTime)
    title = db.Column(db.String(240))
    neighborhood = db.Column(db.String(240))
    address = db.Column(db.String(240))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    price = db.Column(db.Integer)
    housing_type = db.Column(db.String(80))
    bedrooms = db.Column(db.Float)
    flooring = db.Column(db.String(80))
    is_furnished = db.Column(db.Boolean)
    no_smoking = db.Column(db.Boolean)
    ft2 = db.Column(db.Integer)
    laundry = db.Column(db.String(80))
    parking = db.Column(db.String(80))
    rent_period = db.Column(db.String(80))
    url = db.Column(db.String(240))
    misc = db.Column(db.String(480))
    score = db.Column(db.Float)
    _title_neighborhood = db.Column(db.String(240))

    def __repr__(self):
        return f"CraigslistHousing(id={self.id})"
