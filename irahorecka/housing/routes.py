"""
/irahorecka/housing/routes.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask blueprint to handle routes for *.irahorecka.com/housing*.
"""

from pathlib import Path

from flask import abort, jsonify, render_template, request, session, Blueprint

from irahorecka import limiter
from irahorecka.api import read_craigslist_housing, AREAS
from irahorecka.exceptions import ValidationError
from irahorecka.housing.utils import (
    get_area_key,
    get_neighborhoods,
    parse_form,
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
        "profile_img": "me_arrow.png",
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
    Returns Craigslist Housing content sorted by newest posts."""
    query_params = session["query_params"] = parse_form(request.form)
    sort_by = session["sort_by"] = "date_desc"
    limit = session["limit"] = 50
    offset = session["offset"] = 0
    return render_housing_table("housing/table.html", query_params, sort_by, limit, offset)


@housing.route("/housing/query/score", methods=["POST"])
def query_score():
    """Handles rendering of template from HTMX call to /housing/query/score.
    Returns Craigslist Housing content sorted by score value."""
    query_params = session["query_params"] = parse_form(request.form)
    sort_by = session["sort_by"] = "score_desc"
    limit = session["limit"] = 50
    offset = session["offset"] = 0
    return render_housing_table("housing/table.html", query_params, sort_by, limit, offset)


@housing.route("/housing/query/infinite-scroll")
def query_infinite_scroll():
    """Handles rendering of template from HTMX call to /housing/query/infinite-scroll.
    Returns chunked Craigslist Housing content as table rows with number of rows equivalent
    to the 'limit' parameter passed from `query_new` or `query_score`."""
    # Parameters from Flask session.
    query_params = session["query_params"]
    limit = session["limit"]
    offset = session["offset"] = session["limit"] + session["offset"]
    sort_by = session["sort_by"]
    return render_housing_table("housing/tbody.html", query_params, sort_by, limit, offset)


def render_housing_table(html_path, query_params, sort_by, limit, offset):
    """Fetches caller's query from the CraigslistHousing table in database and renders and
    updates housing table from the provided HTML path."""
    # Fetches minified posts.
    posts = list(read_craigslist_housing(query_params, sort_by=sort_by, limit=limit, offset=offset, minified=True))
    content = {
        "posts": tidy_posts(posts),
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
    }
    return render_template(html_path, content=content)


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
        "title": "API Docs: Housing",
        "profile_img": "me_arrow.png",
        "docs": DOCS,
    }
    return render_template("housing/docs.html", content=content)
