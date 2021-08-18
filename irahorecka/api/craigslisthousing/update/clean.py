"""
/irahorecka/api/craigslisthousing/update/clean.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to clean Craigslist housing database table.
"""

import concurrent.futures
import datetime

# Keep `cchardet` and `lxml` imported - used under the hood
import cchardet
import lxml
import httpx
from bs4 import BeautifulSoup, SoupStrainer
from sqlalchemy.sql import func, and_

from irahorecka.models import db, CraigslistHousing


def clean_craigslist_housing():
    """ENTRY POINT: Cleans Craigslist housing database table. To be ran after every
    write to database with new Craigslist housing posts."""
    # Tack on more functions as you see fit. The order of function calls should not be order-dependent.
    rm_old_posts()
    rm_duplicate_posts()
    rm_scam_warning_posts()
    rm_private_bedrooms_posts()
    rm_low_price_posts()


def rm_old_posts(days=7):
    """Removes posts where `CraigslistHousing.last_updated` is over `days` days old."""
    lower_dttm_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
    CraigslistHousing.query.filter(CraigslistHousing.last_updated < lower_dttm_threshold).delete(
        synchronize_session="fetch"
    )
    db.session.commit()


def rm_duplicate_posts():
    """Filters IDs where `CraigslistHousing._title_neighborhood` is unique. This prevents reposts
    by users via a different posting ID."""
    unique_posts = CraigslistHousing.query.with_entities(CraigslistHousing.id).distinct(
        CraigslistHousing._title_neighborhood
    )
    duplicate_posts = CraigslistHousing.__table__.delete().where(CraigslistHousing.id.not_in(unique_posts))
    # Remove duplicate posts
    db.session.execute(duplicate_posts)
    db.session.commit()


def rm_scam_warning_posts():
    """Removes posts where 'scam' is in the post title (case-insensitive). These posts usually warn
    buyers of scammy Craigslist posts."""
    CraigslistHousing.query.filter(func.lower(CraigslistHousing.title).contains("scam")).delete(
        synchronize_session="fetch"
    )
    db.session.commit()


def rm_private_bedrooms_posts():
    """Removes housing posts where price / bedrooms <= 600 USD. Studio posts (i.e. bedrooms == 0)
    are ignored."""
    posts = CraigslistHousing.query.filter(and_(CraigslistHousing.price > 0, CraigslistHousing.bedrooms > 0))
    posts.filter(CraigslistHousing.price / CraigslistHousing.bedrooms <= 600).delete(synchronize_session="fetch")
    db.session.commit()


def rm_low_price_posts():
    """Removes posts where `price` is less than 700 USD."""
    CraigslistHousing.query.filter(CraigslistHousing.price < 700).delete(synchronize_session="fetch")
    db.session.commit()


def rm_expired_craigslist_housing():
    """ENTRY POINT: Removes expired Craigslist housing posts from database. To be ran less
    frequently than `clean_craigslist_housing` as it is time consuming. Advised to run nightly."""
    ids = [post.id for post in CraigslistHousing.query.all()]
    urls = [post.url for post in CraigslistHousing.query.all()]
    session = httpx.Client()
    # Must iterables that are equal in length to rows in `CraigslistHousing`.
    sessions = [session for _ in range(len(urls))]
    strainer = get_cl_strainer()
    strainers = [strainer for _ in range(len(urls))]

    args = tuple(zip(ids, urls, sessions, strainers))
    # Dispatch tasks to multiple threads.
    for post in map_threads(post_is_expired, args):
        if post["is_expired"]:
            CraigslistHousing.query.filter(CraigslistHousing.id == post["id"]).delete(synchronize_session="fetch")

    db.session.commit()


def post_is_expired(args):
    """Checks if Craigslist housing post is expired."""
    id_, url, session, strainer = args
    soup = BeautifulSoup(session.get(url).text, "lxml", parse_only=strainer)
    return {
        "id": id_,
        "is_expired": bool(
            soup.find_all("h2")
            # Searches for keywords 'deleted', 'expired', and 'flagged'.
            and any(keyword in str(soup.find_all("h2")[0]) for keyword in ("deleted", "expired", "flagged"))
        ),
    }


def get_cl_strainer():
    """Gets bs4.SoupStrainer object, targeting relevant elements and attributes of a Craigslist
    post's HTML document."""

    def target_elem_attrs(elem, attrs):
        """Gets desired element and attributes."""
        return elem == "h2"

    return SoupStrainer(target_elem_attrs)


def map_threads(func, _iterable):
    """Maps function with iterable object in using thread pools."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(func, _iterable)
    return result
