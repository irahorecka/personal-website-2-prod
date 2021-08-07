"""
/irahorecka/housing/routes.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask blueprint to handle routes for *.irahorecka.com/housing*.
"""

from datetime import datetime
from pathlib import Path

from flask import abort, jsonify, render_template, request, Blueprint

from irahorecka import limiter
from irahorecka.api import read_craigslist_housing, AREAS
from irahorecka.exceptions import ValidationError
from irahorecka.housing.utils import (
    get_area_key,
    get_neighborhoods,
    parse_req_form,
    read_json,
    tidy_posts,
)

housing = Blueprint("housing", __name__)
DOCS = read_json(Path(__file__).absolute().parent.joinpath("docs.json"))
REGISTERED_APIS = read_json(Path(__file__).absolute().parent.joinpath("api.json"))


@housing.route("/housing")
def index():
    """Landing page of irahorecka.com/housing."""
    content = {
        "title": "Housing",
        "profile_img": "me-arrow.png",
        "area": AREAS,
    }
    return render_template("housing/index.html", content=content)


@housing.route("/housing/neighborhoods", methods=["POST"])
def neighborhoods():
    """Takes user selection of region and returns neighborhoods within selection.
    Notice the routing, it is outside of /housing. This is because neighborhoods are agnostic
    to classified listings' categories."""
    area_key = get_area_key(request.form.get("area", "").lower())
    return render_template("housing/neighborhoods.html", neighborhoods=get_neighborhoods(area_key))


@housing.route("/housing/query/new", methods=["POST"])
def query_new():
    """Handles rendering of template from HTMX call to /housing/query/new.
    Returned content sorted by newest posts."""
    parsed_params = parse_req_form(request.form)
    # Fetch minified posts - don't need all that info.
    posts = list(read_craigslist_housing(parsed_params, minified=True))
    return render_template(
        "housing/table.html",
        posts=sorted(
            tidy_posts(posts), key=lambda x: datetime.strptime(x["last_updated"], "%Y-%m-%d %H:%M"), reverse=True
        ),
    )


@housing.route("/housing/query/score", methods=["POST"])
def query_score():
    """Handles rendering of template from HTMX call to /housing/query/score.
    Returned content sorted by score value."""
    parsed_params = parse_req_form(request.form)
    posts = list(read_craigslist_housing(parsed_params, minified=True))
    return render_template(
        "housing/table.html", posts=sorted(tidy_posts(posts), key=lambda x: x["score"], reverse=True)
    )


#  ~~~~~~~~~~ BEGIN RESTFUL API AND API DOCS ~~~~~~~~~~


@housing.route("/housing/<site>", subdomain="api")
@limiter.limit("10/second")
def api_site(site):
    """REST-like API for Craigslist housing - querying with Craigslist site."""
    # If `site` endpoint is not registered, return 404 response.
    if site not in REGISTERED_APIS:
        abort(404)
    params = {**{"site": site}, **request.args.to_dict()}
    try:
        posts = list(read_craigslist_housing(params))
        return jsonify(posts)
    except ValidationError as e:
        abort(400, str(e))


@housing.route("/housing/<site>/<area>", subdomain="api")
@limiter.limit("10/second")
def api_site_area(site, area):
    """REST-like API for Craigslist housing - querying with Craigslist site
    and area."""
    # If `area` endpoint is not registered within its site, return 404 response.
    if area not in REGISTERED_APIS.get(site, []):
        abort(404)
    params = {**{"site": site, "area": area}, **request.args.to_dict()}
    try:
        posts = list(read_craigslist_housing(params))
        return jsonify(posts)
    except ValidationError as e:
        abort(400, str(e))


@housing.route("/housing", subdomain="docs")
def docs():
    """Documentation page for the housing API."""
    content = {
        "title": "API Documentation: Housing",
        "profile_img": "me-arrow.png",
        "docs": DOCS,
    }
    return render_template("housing/docs.html", content=content)
