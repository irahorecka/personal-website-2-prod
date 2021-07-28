"""
"""

import numpy as np
from sqlalchemy.sql import func, and_

from irahorecka.models import db, CraigslistHousing


def write_craigslist_housing_score(site, areas):
    """ENTRY POINT: Assigns and writes Craigslist housing value scores to posts. Posts
    without a score are left as N/A."""
    query = preliminary_filter(CraigslistHousing, CraigslistHousing.query)
    query_site = query.filter(CraigslistHousing.site == site)
    query_site_ft2 = query_site.filter(CraigslistHousing.ft2 != 0)
    query_site_sans_ft2 = query_site.filter(CraigslistHousing.ft2 == 0)

    for area in areas:
        query_area = query_site.filter(CraigslistHousing.area == area)
        query_area_ft2 = query_site_ft2.filter(CraigslistHousing.area == area)
        query_area_sans_ft2 = query_site_sans_ft2.filter(CraigslistHousing.area == area)

        # Calculate score for posts with price and ft2
        with Ft2(CraigslistHousing, query_site_ft2, query_area_ft2) as ft2:
            ft2.write_score(query_area_ft2)
        # Posts with and without filters are scored differently - normalize scores before grouping
        normalize_score(CraigslistHousing, query_area_ft2, -100, 100)
        # Calculate score for posts with price without ft2
        with Bedrooms(CraigslistHousing, query_site, query_area) as bedrooms:
            bedrooms.write_score(query_area_sans_ft2)
        # Posts without ft2 have scores not as effective as posts with ft2 - set range to -90, 90
        normalize_score(CraigslistHousing, query_area_sans_ft2, -90, 90)

    # Set null scores to 0 to maintain num datatype
    query_site.filter(CraigslistHousing.score.is_(None)).update({CraigslistHousing.score: 0})
    db.session.commit()


def preliminary_filter(model, query):
    """Performs preliminary filters to a query and model. Use to clean up query prior to performing
    statistical analysis."""
    # If 'studio' anywhere in the title, force bedrooms to reflect studio property.
    query.filter(func.lower(model.title).contains("studio")).update({model.bedrooms: 0}, synchronize_session="fetch")
    return query


class Score:
    """Base class for calculating score of a post."""

    def __init__(self, model, query_site, query_area):
        # `query_area` must be a child query of `query_site`
        self.model = model
        self.query_site = query_site
        self.query_area = query_area

    def __enter__(self):
        """Set up instance to have subsequent queries work with 0.5 bedrooms instead of 0.
        This is for the scoring criteria in `_calculate_post_score`, where we deal with the
        logarithms of the number of bedrooms."""
        self.query_site.filter(self.model.bedrooms == 0).update({self.model.bedrooms: 0.5})
        self.query_area.filter(self.model.bedrooms == 0).update({self.model.bedrooms: 0.5})
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Set queries with 0.5 bedrooms (from `__enter__`) to 0 and set null scores to 0."""
        self.query_site.filter(self.model.bedrooms == 0.5).update({self.model.bedrooms: 0})
        self.query_area.filter(self.model.bedrooms == 0.5).update({self.model.bedrooms: 0})

    def _calculate_post_score(self, site_z_score, area_z_score):
        """Calculates value score for every post. Read description below for calc breakdown:
        - Calculate AVG, STDEV price/sqft for posts within site and area.
            - Area value is multiplied with 0.2 coefficient, Site value with 0.7 coefficient.
        - Score equation:
            = 0.25 * (1 - (0.25 * stdev_within_area)) + 0.65 * (1 - (0.65 * stdev_within_bayarea)) + 0.1 * (1 + math.log(num_bedrooms)) - 1
        - Purely average post should equate to a score of 1.0, meaning average price within Site, Area, and has 1 bedroom.
        - Score more than 0 is GOOD, less than 0 is BAD."""
        site_weight = 0.25 * (1 - (0.25 * site_z_score))
        area_weight = 0.65 * (1 - (0.65 * area_z_score))
        bedroom_weight = 0.1 * (1 + func.log(self.model.bedrooms))
        # Subtract 1, which is the neutral score
        return site_weight + area_weight + bedroom_weight - 1

    @staticmethod
    def _get_output_within_percentile(fn, *args, perc_min=5, perc_max=95):
        """Takes lower and upper percentile limit and returns a tuple of lists where the output
        (i.e. fn(arg1, arg2))) is within the specified percentile range."""
        output = fn(*args)
        low = np.percentile(output, perc_min)
        high = np.percentile(output, perc_max)
        desired_percentile = np.where(np.logical_and(output >= low, output <= high))
        return output[desired_percentile]


class Ft2(Score):
    """Calculates score for posts with ft2 attribute. Inherits from `Score`."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write_score(self, query_write):
        """Writes score to posts in `query_write`."""
        # Filter posts to allow for logarithmic operations
        query_write = self._filter_query_for_log_calc(query_write)
        summary = self._get_log_postvalue_summary()
        log_postvalue = func.log(
            self._postvalue_fn(func.log, func.sqrt, self.model.price, self.model.ft2, self.model.bedrooms)
        )
        site_z_score = (log_postvalue - summary["site_avg_log_postvalue"]) / summary["site_std_log_postvalue"]
        area_z_score = (log_postvalue - summary["area_avg_log_postvalue"]) / summary["area_std_log_postvalue"]
        query_write.update(
            {self.model.score: self._calculate_post_score(site_z_score, area_z_score)}, synchronize_session="fetch"
        )

    def _get_log_postvalue_summary(self):
        """Gets summary average and standard deviation of log(postvalue) for posts in site
        and area with a non-zero value in price / ft2."""
        postvalue_site = self._get_postvalue_spread(self.query_site)
        postvalue_area = self._get_postvalue_spread(self.query_area)
        return {
            "site_avg_log_postvalue": np.average(np.log(postvalue_site)),
            "area_avg_log_postvalue": np.average(np.log(postvalue_area)),
            "site_std_log_postvalue": np.std(np.log(postvalue_site)),
            "area_std_log_postvalue": np.std(np.log(postvalue_area)),
        }

    def _get_postvalue_spread(self, query):
        """Takes posts within a percentile range of a post's value (algorithm defined in
        `self._postvalue_fn`) from a given query. This function's intention is to gather the spread
        of the posts' values."""
        # Remove posts where price / ft2 <= 0 and ft2 <= 1
        query = self._filter_query_for_log_calc(query)
        price, ft2, bedrooms = map(
            lambda x: (np.array(x)), zip(*[(post.price, post.ft2, post.bedrooms) for post in query.all()])
        )
        # Gets posts' price / ft2 values (`np.array`) that are within 5% - 95% percentile
        return self._get_output_within_percentile(
            self._postvalue_fn, np.log, np.sqrt, price, ft2, bedrooms, perc_min=5, perc_max=95
        )

    def _postvalue_fn(self, log_fn, sqrt_fn, price, ft2, bedrooms):
        return log_fn(log_fn(price) / sqrt_fn(bedrooms)) * price / sqrt_fn(ft2)

    def _filter_query_for_log_calc(self, query):
        """Update query to select for self.model.price / self.model.ft2 > 0 to allow for logarithmic calc."""
        return query.filter(
            and_(
                self.model.price / func.sqrt(self.model.ft2) > 0,
                func.log(self.model.price) / func.sqrt(self.model.ft2) > 0,
            )
        )


class Bedrooms(Score):
    """Calculates score for posts without ft2 attribute. Inherits from `Score`."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write_score(self, query_write):
        """Writes score to posts in `query_write`."""
        # Filter posts to allow for logarithmic operations
        query_write = self._filter_query_for_log_calc(query_write)
        summary = self._get_log_postvalue_summary()
        log_postvalue = func.log(self._postvalue_fn(func.log, self.model.price, self.model.bedrooms))
        site_z_score = (log_postvalue - summary["site_avg_log_postvalue"]) / summary["site_std_log_postvalue"]
        area_z_score = (log_postvalue - summary["area_avg_log_postvalue"]) / summary["area_std_log_postvalue"]
        query_write.update(
            {self.model.score: self._calculate_post_score(site_z_score, area_z_score)}, synchronize_session="fetch"
        )

    def _get_log_postvalue_summary(self):
        """Gets summary average and standard deviation of log(postvalue) for posts in site
        and area with a non-zero value in bedrooms and price."""
        postvalue_site = self._get_postvalue_spread(self.query_site)
        postvalue_area = self._get_postvalue_spread(self.query_area)
        return {
            "site_avg_log_postvalue": np.average(np.log(postvalue_site)),
            "area_avg_log_postvalue": np.average(np.log(postvalue_area)),
            "site_std_log_postvalue": np.std(np.log(postvalue_site)),
            "area_std_log_postvalue": np.std(np.log(postvalue_area)),
        }

    def _get_postvalue_spread(self, query):
        """Takes posts within a percentile range of a post's value (algorithm defined in
        `self._postvalue_fn`) from a given query. This function's intention is to gather the spread
        of the posts' values."""
        # Filter for bedrooms to be within 0 - 7 range. Filter for price > 0.
        query = self._filter_query_for_log_calc(query)
        price, bedrooms = map(lambda x: (np.array(x)), zip(*[(post.price, post.bedrooms) for post in query.all()]))
        # Gets posts' value that are within 5% - 95% percentile
        return self._get_output_within_percentile(self._postvalue_fn, np.log, price, bedrooms, perc_min=5, perc_max=95)

    @staticmethod
    def _postvalue_fn(log_fn, price, bedrooms):
        """An algorithm to evaluate housing value from price and number of bedrooms."""
        return (price + (price * (1 - log_fn(bedrooms)))) / 2

    def _filter_query_for_log_calc(self, query):
        """Update query to select for self.model.price and self.model.bedrooms > 0 AND
        self.model.bedrooms < 8 to allow for logarithmic calc."""
        return query.filter(and_(self.model.price > 0, self.model.bedrooms > 0, self.model.bedrooms < 8))


def normalize_score(model, query, min_score, max_score):
    """Normalizes score to fall within -100 and +100. of what's low and high, respectively."""
    # Update all model.score value with NoneType to be the average of min and max normalized scores
    query.filter(model.score == 0).update({model.score: (min_score + max_score) / 2})
    # Get query with all numtypes in model.score
    query_num = query.filter(model.score != 0)
    min_q_score, max_q_score = get_min_max_scores(query_num)
    query_num.filter(model.score <= min_q_score).update({model.score: min_score})
    query_num.filter(model.score >= max_q_score).update({model.score: max_score})

    # Get query with model.score within min_q_score and max_q_score
    query_range = query_num.filter(and_(model.score >= min_q_score, model.score <= max_q_score))
    # Equation for normalizing score
    # = (((score - low_score) / (high_score - low_score)) * (2 * max_score)) + min_score
    normalized_score = ((model.score - min_q_score) / (max_q_score - min_q_score)) * (2 * max_score) + min_score
    # Round normalized score to the nearest 5
    query_range.update({model.score: func.round(normalized_score * 0.2) / 0.2})


def get_min_max_scores(query):
    """To be called after binding score to posts. Normalizes score to more user friendly values.
    See `normalize_score`. Input query where query.score is all numerics."""
    scores = np.array([post.score for post in query.all()])
    # Takes scores within 0.75% to 99.25% percentile - sets these as absolute min and max, respectively
    low = np.percentile(scores, 0.75)
    high = np.percentile(scores, 99.25)
    return low, high
