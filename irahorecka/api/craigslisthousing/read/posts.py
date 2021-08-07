"""
/irahorecka/api/craigslisthousing/read/posts.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to handle the validation and delivery of Craigslist posts from a query.
"""

from datetime import datetime

from cerberus import Validator

from irahorecka.exceptions import ValidationError
from irahorecka.models import CraigslistHousing


def read_craigslist_housing(request_args, minified=False):
    """ENTRY POINT: Reads query and yields Craigslist housing posts as dictionaries from database."""
    v_status, v_args = validate_request_args(request_args)
    # Raise ValidationError to caller if parsing of request args failed
    if not v_status:
        raise ValidationError(v_args)
    # Set maximum limit to 3000 per call. Ensure limit is a positive value else limit is 0.
    limit = min(max(v_args["limit"], 0), 3_000)
    filtered_query = filter_query(CraigslistHousing, v_args)
    if not minified:
        yield from fetch_content(CraigslistHousing, filtered_query, limit)
    else:
        yield from fetch_content_minified(CraigslistHousing, filtered_query, limit)


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


def filter_query(model, validated_args):
    """Returns filtered db.Model.query object to caller, filtered by arguments in `validated_args`."""
    # If an ID was provided in the query, return post with ID immediately.
    if validated_args.get("id"):
        return tuple(model.query.get(validated_args["id"]))
    query = filter_categorical(model, model.query, validated_args)
    return filter_scalar(model, query, validated_args)


def filter_categorical(model, query, validated_args):
    """Filters categorical attributes of the requests query.
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
        query = query.filter(getattr(model, attr).like("%%%s%%" % value))
    return query


def filter_scalar(model, query, validated_args):
    """Filters scalar attributes of the requests query. E.g. `min_price=1000`."""
    return (
        query.filter(model.bedrooms >= validated_args["min_bedrooms"])
        .filter(model.bedrooms <= validated_args["max_bedrooms"])
        .filter(model.ft2 >= validated_args["min_ft2"])
        .filter(model.ft2 <= validated_args["max_ft2"])
        .filter(model.price >= validated_args["min_price"])
        .filter(model.price <= validated_args["max_price"])
    )


def fetch_content(model, query, limit):
    """Fetches posts from the database with detailed content."""
    # Apparently, instantiation of a model object is negated if we work with entities
    # because we work with tuples of column data - good for speed.
    # fmt: off
    posts = query.with_entities(
        model.id, model.repost_of, model.last_updated, model.url, model.site, model.area,
        model.neighborhood, model.address, model.lat, model.lon, model.title, model.price,
        model.housing_type, model.bedrooms, model.flooring, model.is_furnished, model.no_smoking,
        model.ft2, model.laundry, model.rent_period, model.parking, model.misc, model.score,
    )
    # fmt: on
    for idx, post in enumerate(posts):
        if idx == limit:
            return
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


def fetch_content_minified(model, query, limit):
    """Fetches posts from the database with minified content."""
    posts = query.with_entities(model.last_updated, model.url, model.title, model.price, model.bedrooms, model.score)
    for idx, post in enumerate(posts):
        if idx == limit:
            return
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
