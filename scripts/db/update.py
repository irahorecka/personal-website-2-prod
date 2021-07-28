import irahorecka.api as api


def update_github(app):
    with app.app_context():
        # Update database with GitHub information
        api.write_github_repos()


def update_housing(app):
    with app.app_context():
        # Update database with Craigslist Housing information
        # The following sequences must go in this order
        api.write_craigslist_housing(site="sfbay", areas=["eby", "nby", "sby", "sfc", "pen", "scz"])
        api.clean_craigslist_housing()


def update_housing_score(app):
    with app.app_context():
        # Update Craigslist Housing table with post scores
        api.write_craigslist_housing_score(site="sfbay", areas=["eby", "nby", "sby", "sfc", "pen", "scz"])
