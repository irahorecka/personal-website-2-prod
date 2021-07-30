"""
/irahorecka/routes.py
Ira Horecka - July 2021
~~~~~~~~~~~~~~~~~~~~~~~

#
"""
from pathlib import Path

import yaml
from flask import render_template, Blueprint

from irahorecka.api import read_github_repos

main = Blueprint("main", __name__)
with open(Path(__file__).absolute().parent.parent.parent / "config.yaml", "r") as config:
    GITHUB_REPOS = yaml.safe_load(config)["github-repos"]


@main.route("/home")
@main.route("/")
def home():
    """Landing page of personal website."""
    content = {
        "title": "Home",
        "profile_img": "profile.png",
    }
    return render_template("index.html", content=content)


@main.route("/projects")
def projects():
    """GitHub projects page of personal website."""
    content = {
        "title": "Projects",
        "profile_img": "me_computing.png",
        "repos": read_github_repos(GITHUB_REPOS),
    }
    return render_template("projects.html", content=content)
