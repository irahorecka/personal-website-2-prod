"""
Clean db of junk data
Criteria:
- Posts older than a week of cleaning
- Repeated titles per given neighborhood in database
- Posts with price < $300
"""

import concurrent.futures
import datetime

import cchardet
import lxml
import httpx
from bs4 import BeautifulSoup, SoupStrainer

from irahorecka.models import db, CraigslistHousing


def clean_craigslist_housing():
    """ENTRY POINT: Cleans Craigslist Housing database."""
    # Tack on more functions as you see fit.
    rm_old_posts()
    rm_duplicate_posts()
    rm_low_prices()


def rm_old_posts(days=7):
    """Removes posts where `CraigslistHousing.last_updated` is over `days` old."""
    lower_dttm_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
    CraigslistHousing.query.filter(CraigslistHousing.last_updated < lower_dttm_threshold).delete()
    db.session.commit()


def rm_duplicate_posts():
    """Filters id's where `CraigslistHousing._title_neighborhood` is unique."""
    unique_posts = CraigslistHousing.query.with_entities(CraigslistHousing.id).distinct(
        CraigslistHousing._title_neighborhood
    )
    duplicate_posts = CraigslistHousing.__table__.delete().where(CraigslistHousing.id.not_in(unique_posts))
    # Remove duplicate posts
    db.session.execute(duplicate_posts)
    db.session.commit()


def rm_low_prices():
    """Removes posts where `price` is less than 300"""
    CraigslistHousing.query.filter(CraigslistHousing.price < 300).delete()
    db.session.commit()


def rm_expired_craigslist_housing():
    """ENTRY POINT: Removes expired Craigslist Housing posts from database."""
    ids = [post.id for post in CraigslistHousing.query.all()]
    urls = [post.url for post in CraigslistHousing.query.all()]
    session = httpx.Client()
    sessions = [session for _ in range(len(urls))]
    strainer = get_cl_strainer()
    strainers = [strainer for _ in range(len(urls))]

    args = tuple(zip(ids, urls, sessions, strainers))
    for post in map_threads(post_is_expired, args):
        if post["is_expired"]:
            CraigslistHousing.query.filter(CraigslistHousing.id == post["id"]).delete()

    db.session.commit()


def post_is_expired(args):
    """Checks if Craigslist post is expired."""
    id_, url, session, strainer = args
    soup = BeautifulSoup(session.get(url).text, "lxml", parse_only=strainer)
    return {
        "id": id_,
        "is_expired": bool(
            soup.find_all("h2")
            and any(keyword in str(soup.find_all("h2")[0]) for keyword in ("deleted", "expired", "flagged"))
        ),
    }


def get_cl_strainer():
    """Gets bs4.SoupStrainer object, targeting relevant sections of the Craigslist page."""

    def target_elem_attrs(elem, attrs):
        """Gets desired element from Craigslist HTML document."""
        if elem == "h2":
            return True

    return SoupStrainer(target_elem_attrs)


def map_threads(func, _iterable):
    """Map function with iterable object in using thread pools."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(func, _iterable)
    return result
