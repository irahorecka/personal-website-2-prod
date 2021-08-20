"""
/irahorecka/api/craigslisthousing/read/posts.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to handle the validation and delivery of Craigslist posts from a query.
"""

from datetime import datetime

from cerberus import Validator

from irahorecka.exceptions import ValidationError
from irahorecka.models import CraigslistHousing


def read_craigslist_housing(request_args, sort_by=None, limit=None, offset=None, minified=False):
    """ENTRY POINT: Reads query and yields Craigslist housing posts as dictionaries from database."""
    # If there is a limit kwarg other than None, create or override request_args["limit"]
    if limit is not None:
        request_args["limit"] = limit
    v_status, v_args = validate_request_args(request_args)
    # Raise ValidationError to caller if parsing of request args failed
    if not v_status:
        raise ValidationError(v_args)
    # Set maximum limit to 3000 per call. Ensure limit is a positive value else limit is 0.
    limit = min(max(v_args["limit"], 0), 3_000)
    filtered_query = fetch_housing_query(v_args)
    # Sort query by using sorting keys found in `sort_housing_query`.
    # E.g. `date_desc` --> sort posts' datetime in descending order.
    sorted_query = sort_housing_query(filtered_query, sort_by)
    if not minified:
        yield from fetch_housing_content(sorted_query, limit, offset)
    else:
        yield from fetch_housing_content_minified(sorted_query, limit, offset)


def validate_request_args(request_args):
    """Validates request args for proper data types. Coerce into desired datatype if initial
    validation passes, otherwise send error code and failure message to be returned to caller."""
    # Declare schema within function - usually single query, single validation.
    # Avoid worrying about performance impact from declaration.
    schema = {
        "id": {"type": "integer", "coerce": int, "default": 0},
        # Cast to float then try to validate as integer. Set default limit to 50 posts per query.
        "limit": {"type": "integer", "coerce": (float, int), "default": 50},
        "area": {"type": "string", "default": ""},
        "site": {"type": "string", "default": ""},
        "neighborhood": {"type": "string", "default": ""},
        "housing_type": {"type": "string", "default": ""},
        "laundry": {"type": "string", "default": ""},
        "parking": {"type": "string", "default": ""},
        "min_bedrooms": {"type": "integer", "coerce": (float, int), "default": 0},
        "max_bedrooms": {"type": "integer", "coerce": (float, int), "default": 10},
        "min_ft2": {"type": "integer", "coerce": (float, int), "default": 0},
        "max_ft2": {"type": "integer", "coerce": (float, int), "default": 1_000_000},
        "min_price": {"type": "integer", "coerce": (float, int), "default": 0},
        "max_price": {"type": "integer", "coerce": (float, int), "default": 100_000},
    }
    v = Validator(schema)
    if not v.validate(request_args):
        return (False, v.errors)
    return (True, v.normalized(request_args))


def fetch_housing_query(validated_args):
    """Returns filtered CraigslistHousing.query object to caller filtered by arguments in `validated_args`."""
    # If an ID was provided in the query, return post with ID immediately.
    if validated_args.get("id"):
        # Not optimal in performance, but conforms to datatype of non-id-based queries.
        return CraigslistHousing.query.filter(CraigslistHousing.id == validated_args["id"])
    query = filter_categorical(CraigslistHousing.query, validated_args)
    return filter_scalar(query, validated_args)


def filter_categorical(query, validated_args):
    """Filters CraigslistHousing categorical attributes from the requests query.
    E.g. `neighborhood=fremont / union city / newark`."""
    categorical_filter = {
        "area": validated_args["area"],
        "site": validated_args["site"],
        "neighborhood": validated_args["neighborhood"],
        "housing_type": validated_args["housing_type"],
        "laundry": validated_args["laundry"],
        "parking": validated_args["parking"],
    }
    for attr, value in categorical_filter.items():
        query = query.filter(getattr(CraigslistHousing, attr).like("%%%s%%" % value))
    return query


def filter_scalar(query, validated_args):
    """Filters CraigslistHousing scalar attributes from the requests query.
    E.g. `min_price=1000`."""
    return (
        query.filter(CraigslistHousing.bedrooms >= validated_args["min_bedrooms"])
        .filter(CraigslistHousing.bedrooms <= validated_args["max_bedrooms"])
        .filter(CraigslistHousing.ft2 >= validated_args["min_ft2"])
        .filter(CraigslistHousing.ft2 <= validated_args["max_ft2"])
        .filter(CraigslistHousing.price >= validated_args["min_price"])
        .filter(CraigslistHousing.price <= validated_args["max_price"])
    )


def sort_housing_query(query, sort_by):
    """Sorts CraigslistHousing query by CraigslistHousing attributes via sort_by keys.
    The established keys are: 'date_asc', 'date_desc', 'score_asc', and 'score_desc'."""
    sort_expr = {
        "date_asc": lambda q: q.order_by(CraigslistHousing.last_updated.asc()),
        "date_desc": lambda q: q.order_by(CraigslistHousing.last_updated.desc()),
        "score_asc": lambda q: q.order_by(CraigslistHousing.score.asc()),
        "score_desc": lambda q: q.order_by(CraigslistHousing.score.desc()),
    }
    if not sort_expr.get(sort_by):
        return query
    return sort_expr[sort_by](query)


def fetch_housing_content(query, limit, offset):
    """Fetches CraigslistHousing data from database with detailed content."""
    # Apparently, instantiation of a CraigslistHousing object is negated if we work with entities
    # because we work with tuples of column data - good for speed.
    # fmt: off
    posts = query.with_entities(
        CraigslistHousing.id, CraigslistHousing.repost_of, CraigslistHousing.last_updated, CraigslistHousing.url,
        CraigslistHousing.site, CraigslistHousing.area, CraigslistHousing.neighborhood, CraigslistHousing.address,
        CraigslistHousing.lat, CraigslistHousing.lon, CraigslistHousing.title, CraigslistHousing.price,
        CraigslistHousing.housing_type, CraigslistHousing.bedrooms, CraigslistHousing.flooring, CraigslistHousing.is_furnished,
        CraigslistHousing.no_smoking, CraigslistHousing.ft2, CraigslistHousing.laundry, CraigslistHousing.rent_period,
        CraigslistHousing.parking, CraigslistHousing.misc, CraigslistHousing.score,
    ).limit(limit).offset(offset)
    # fmt: on
    for post in posts:
        yield {
            # Metadata
            "id": post.id,
            "repost_of": post.repost_of,
            "last_updated": datetime.strftime(post.last_updated, "%Y-%m-%d %H:%M"),
            "url": post.url,
            # Location
            "site": post.site,
            "area": post.area,
            "neighborhood": post.neighborhood,
            "address": post.address,
            "lat": post.lat,
            "lon": post.lon,
            # Post
            "title": post.title,
            "price": f"${post.price}",
            "housing_type": post.housing_type,
            # Bedrooms in model is float type.
            "bedrooms": int(post.bedrooms),
            "flooring": post.flooring,
            "is_furnished": post.is_furnished,
            "no_smoking": post.no_smoking,
            "ft2": post.ft2,
            "laundry": post.laundry,
            "rent_period": post.rent_period,
            "parking": post.parking,
            "misc": post.misc.split(";"),
            # Score in model is float type.
            "score": int(post.score),
        }


def fetch_housing_content_minified(query, limit, offset):
    """Fetches CraigslistHousing data from database with minified content."""
    # fmt: off
    posts = query.with_entities(
        CraigslistHousing.last_updated, CraigslistHousing.url, CraigslistHousing.title, CraigslistHousing.price,
        CraigslistHousing.bedrooms, CraigslistHousing.score,
    ).limit(limit).offset(offset)
    # fmt: on
    for post in posts:
        yield {
            # Metadata
            "last_updated": datetime.strftime(post.last_updated, "%Y-%m-%d %H:%M"),
            "url": post.url,
            # Post
            "title": post.title,
            "price": f"${post.price}",
            "bedrooms": int(post.bedrooms),
            "score": int(post.score),
        }
