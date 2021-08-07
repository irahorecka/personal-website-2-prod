"""
/irahorecka/housing/utils.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utility module to support /irahorecka/housing/routes.py.
"""

import json

from irahorecka.api import AREA_KEYS, NEIGHBORHOODS

SCORE_COLORS = {
    "very-poor": "bg-red-400",
    "poor": "bg-red-300",
    "mild-poor": "bg-red-200",
    "neutral": "bg-white",
    "mild-good": "bg-green-200",
    "good": "bg-green-300",
    "very-good": "bg-green-400",
}


def get_area_key(key):
    """Returns area key read from key provided by caller. Default to empty
    string if key not found."""
    return AREA_KEYS.get(key, "")


def get_neighborhoods(key):
    """Returns an iterable of neighborhoods from key provided by caller."""
    return NEIGHBORHOODS.get(key, tuple())


def get_score_color(score):
    """Gets score color from score provided by caller."""
    if score >= 80:
        return SCORE_COLORS["very-good"]
    if score >= 40:
        return SCORE_COLORS["good"]
    if score > 0:
        return SCORE_COLORS["mild-good"]
    if score <= -80:
        return SCORE_COLORS["very-poor"]
    if score <= -40:
        return SCORE_COLORS["poor"]
    if score < 0:
        return SCORE_COLORS["mild-poor"]
    return SCORE_COLORS["neutral"]


def parse_req_form(request_form):
    """Parses request form provided by caller and returns parameters dict."""
    params = {key: value.lower() for key, value in request_form.items() if value and value not in ["-"]}
    if params.get("area"):
        params["area"] = get_area_key(params["area"])
    return params


def tidy_posts(posts):
    """Tidies an iterable of posts provided by caller. Currently the only tidiness is
    adding score color key based on the provided score."""
    for post in posts:
        post["score_color"] = get_score_color(post["score"])
    return posts


def read_json(path):
    """Returns JSON file as dictionary."""
    with open(path) as file:
        content = json.load(file)
    return content
