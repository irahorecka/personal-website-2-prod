"""
/irahorecka/api/__init__.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Concerns all things API (read, write, update).
"""

import os
from functools import partial

from dotenv import load_dotenv

from irahorecka.api.craigslisthousing.read.posts import read_craigslist_housing
from irahorecka.api.craigslisthousing.read.neighborhood import read_neighborhoods
from irahorecka.api.craigslisthousing.write.posts import write_craigslist_housing
from irahorecka.api.craigslisthousing.update.clean import clean_craigslist_housing, rm_expired_craigslist_housing
from irahorecka.api.craigslisthousing.update.score import write_craigslist_housing_score
from irahorecka.api.githubrepos.read import read_github_repos
from irahorecka.api.githubrepos.write import write_github_repos

load_dotenv()

NEIGHBORHOODS = read_neighborhoods()
# Sourced from python-craigslist-meta.
AREAS = [
    "East Bay Area",
    "North Bay / Marin",
    "Peninsula",
    "City of San Francisco",
    "Santa Cruz Co",
    "South Bay Area",
]
# Set to lower casing for case-agnostic lookups.
AREA_KEYS = {
    "east bay area": "eby",
    "north bay / marin": "nby",
    "peninsula": "pen",
    "south bay area": "sby",
    "santa cruz co": "scz",
    "city of san francisco": "sfc",
}
write_github_repos = partial(write_github_repos, os.environ["GITHUB_TOKEN"])
