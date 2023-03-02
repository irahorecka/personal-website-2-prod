"""
/irahorecka/api/craigslisthousing/write/posts.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to write and update Craigslist housing database table.
"""

import time
from datetime import datetime

import pycraigslist
from pycraigslist.exceptions import ConnectionError
from sqlalchemy import exc

from irahorecka.models import db, CraigslistHousing


def write_craigslist_housing(site, areas=("null",)):
    """ENTRY POINT: Writes Craigslist housing posts (category `apa`) to database."""
    craigslist_housing = fetch_craigslist_apa(site, areas)
    posts = [
        CraigslistHousing(
            id=post["id"],
            site=post.get("site", ""),
            area=post.get("area", "0"),
            repost_of=post.get("repost_of", ""),
            last_updated=datetime.strptime(post["last_updated"], "%Y-%m-%d %H:%M"),
            title=post.get("title", ""),
            neighborhood=post.get("neighborhood", "").lower(),
            address=post.get("address", ""),
            # Coordinates for Guest Peninsula, Antactica if there's no lat or lon.
            lat="-76.299965" if not post.get("lat") else post["lat"],
            lon="-148.003021" if not post.get("lon") else post["lon"],
            # Convert price into numerics: e.g. '$1,500' --> '1500'
            price=post.get("price", "0").replace("$", "").replace(",", ""),
            housing_type=post.get("housing_type", ""),
            bedrooms=post.get("bedrooms", "0"),
            flooring=post.get("flooring", ""),
            is_furnished=bool(post.get("is_furnished")),
            no_smoking=bool(post.get("no_smoking", "false")),
            ft2=post.get("area-ft2", "0"),
            laundry=post.get("laundry", ""),
            parking=post.get("parking", ""),
            rent_period=post.get("rent_period", ""),
            url=post.get("url", ""),
            misc=";".join(post.get("misc", [])),
            _title_neighborhood=f'{post.get("neighborhood", "")}{post.get("title", "")}',
        )
        for post in craigslist_housing
    ]
    try:
        db.session.add_all(posts)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()


def fetch_craigslist_apa(*args, **kwargs):
    """Fetches Craigslist apartments / housing posts."""
    posts = []
    post_id_ref = set()
    for apa in yield_apa(*args, **kwargs):
        for post in apa.search_detail():
            post_id = int(post["id"])
            # Performs checks to ensure no duplication of ID in current search and CraigslistHousing table.
            if post_id in post_id_ref or CraigslistHousing.query.get(post_id):
                continue
            post_id_ref.add(post_id)
            posts.append(post)
            # Don't add to database here, we want to writing to database executed ASAP.
            # i.e. no unnecessary write latency during Craigslist scraping.
    return posts


def yield_apa(site, areas):
    """Yields detailed posts from `pycraigslist.housing.apa` instances."""
    # Attempt to query pycraigslist instances even if there's a connection error.
    for i in range(4):
        try:
            yield from [
                pycraigslist.housing.apa(site=site, area=area, filters=query_filter)
                for area in areas
                for query_filter in yield_apa_filters()
            ]
            # Break out if successfully executed.
            return
        except ConnectionError:
            if i == 3:
                # Raise error if error cannot be resolved in 3 attempts.
                raise ConnectionError from ConnectionError
            # Wait a minute before reattempting query.
            time.sleep(60)


def yield_apa_filters():
    """Yields `pycraigslist.housing.apa` filters for subsequent queries."""
    # Only filter for prices, ranging from $500 - $8000 in $500 increments to gain more listing coverage.
    # Craigslist limits number of posts to 3000 for any given query.
    yield from [
        {"min_price": min_price, "max_price": max_price}
        for min_price, max_price in zip(range(500, 8000, 500), range(1000, 8500, 500))
    ]
