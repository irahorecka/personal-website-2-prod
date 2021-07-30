"""
/irahorecka/routes.py
Ira Horecka - July 2021
~~~~~~~~~~~~~~~~~~~~~~~

#
"""
import random
from datetime import datetime

from flask import jsonify, render_template, request, Blueprint

from irahorecka.api import read_craigslist_housing, AREAS
from irahorecka.exceptions import InvalidUsage, ValidationError
from irahorecka.housing.utils import (
    get_area_key,
    get_neighborhoods,
    parse_req_form,
    read_docs,
    tidy_posts,
)

housing = Blueprint("housing", __name__)


@housing.route("/housing")
def home():
    """API page of personal website."""
    # Set default area and neighborhood per request.
    default_area = random.sample(AREAS, 1).pop()
    default_neighborhood = random.sample(get_neighborhoods(get_area_key(default_area.lower())), 1).pop()
    content = {
        "title": "Housing",
        "profile_img": "me_arrow.png",
        "area": AREAS,
        "default": {
            "area": default_area,
            "neighborhood": default_neighborhood,
        },
    }
    return render_template("housing/index.html", content=content)


@housing.route("/housing/neighborhoods", methods=["POST"])
def neighborhoods():
    """Takes user selection of region and returns neighborhoods within selection.
    Notice the routing, it is outside of /housing. This is because neighborhoods are agnostic
    to classified listings' categories."""
    area_key = get_area_key(request.form.get("area", "").lower())
    return render_template("housing/neighborhoods.html", neighborhoods=get_neighborhoods(area_key))


@housing.route("/housing/query", methods=["POST"])
def query():
    """Handles rendering of template from HTMX call to /housing/query.
    Sort returned content by newest posts."""
    parsed_params = parse_req_form(request.form)
    # Fetch minified posts - don't need all that info.
    posts = list(read_craigslist_housing(parsed_params, minified=True))
    return render_template(
        "housing/table.html",
        posts=sorted(
            tidy_posts(posts), key=lambda x: datetime.strptime(x["last_updated"], "%Y-%m-%d %H:%M"), reverse=True
        ),
    )


@housing.route("/housing/query_score", methods=["POST"])
def query_score():
    """Handles rendering of template from HTMX call to /housing/query_score.
    Sort returned content by score value."""
    parsed_params = parse_req_form(request.form)
    posts = list(read_craigslist_housing(parsed_params, minified=True))
    return render_template(
        "housing/table.html", posts=sorted(tidy_posts(posts), key=lambda x: x["score"], reverse=True)
    )


#  ~~~~~~~~~~ BEGIN RESTFUL API ~~~~~~~~~~


@housing.route("/housing/<site>", subdomain="api")
def api_site(site):
    """REST-like API for Craigslist housing - querying with Craigslist site."""
    params = {**{"site": site}, **request.args.to_dict()}
    try:
        posts = list(read_craigslist_housing(params))
        return jsonify(posts)
    except ValidationError as e:
        raise InvalidUsage(str(e).capitalize(), status_code=400) from e


@housing.route("/housing/<site>/<area>", subdomain="api")
def api_site_area(site, area):
    """REST-like API for Craigslist housing - querying with Craigslist site
    and area."""
    params = {**{"site": site, "area": area}, **request.args.to_dict()}
    try:
        posts = list(read_craigslist_housing(params))
        return jsonify(posts)
    except ValidationError as e:
        raise InvalidUsage(str(e).capitalize(), status_code=400) from e


@housing.route("/housing", subdomain="docs")
def api_docs():
    """Documentation page for personal website's API."""
    content = {
        "title": "API Documentation: Housing",
        "profile_img": "me_arrow.png",
        "docs": read_docs(),
    }
    return render_template("housing/docs.html", content=content)


@housing.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handles invalid usage from REST-like api."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
