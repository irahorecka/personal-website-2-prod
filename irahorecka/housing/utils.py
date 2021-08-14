"""
/irahorecka/housing/utils.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utility module to support /irahorecka/housing/routes.py.
"""

import json

from irahorecka.api import AREA_KEYS, NEIGHBORHOODS


def get_area_key(key):
    """Returns area key read from key provided by caller. Default to empty
    string if key not found."""
    return AREA_KEYS.get(key, "")


def get_neighborhoods(key):
    """Returns an iterable of neighborhoods from key provided by caller."""
    return NEIGHBORHOODS.get(key, tuple())


def get_score_class_and_letter(score):
    """Gets score class (CSS) and score letter from numeric score provided by caller. Take a
    look at irahorecka/static/css/dist/style.css to view these classes. This function assumes
    a score will range from -100 to 100."""
    if score >= 60:
        if score > 86.6:
            return "score-grade-A", "A+"
        if score > 73.3:
            return "score-grade-A", "A"
        return "score-grade-A", "A-"
    if score >= 20:
        if score > 46.6:
            return "score-grade-B", "B+"
        if score > 33.3:
            return "score-grade-B", "B"
        return "score-grade-B", "B-"
    if score >= -20:
        if score > 6.6:
            return "score-grade-C", "C+"
        if score > -6.6:
            return "score-grade-C", "C"
        return "score-grade-C", "C-"
    if score >= -60:
        if score > -33.3:
            return "score-grade-D", "D+"
        if score > -46.6:
            return "score-grade-D", "D"
        return "score-grade-D", "D-"
    return "score-grade-F", "F"


def parse_req_form(request_form):
    """Parses request form provided by caller and returns parameters dict."""
    params = {key: value.lower() for key, value in request_form.items() if value and value not in ["-"]}
    if params.get("area"):
        params["area"] = get_area_key(params["area"])
    return params


def tidy_posts(posts):
    """Tidies an iterable of posts provided by caller. Currently the only tidiness is
    adding score color and letter based on the provided score."""
    for post in posts:
        post["score_class"], post["score_letter"] = get_score_class_and_letter(post["score"])
    return posts


def read_json(path):
    """Returns JSON file as dictionary."""
    with open(path) as file:
        content = json.load(file)
    return content
