"""
/irahorecka/errors/handlers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask blueprint to handle errors.
"""

from flask import request, render_template, Blueprint

from irahorecka.exceptions import InvalidUsage

errors = Blueprint("errors", __name__)


def api_error_reroute(route):
    """Reroutes calls to the api subdomain to return JSONified response.
    I.e. if a call was made to api.irahorecka.com/*"""

    def wrapper(error):
        if request.headers["Host"].startswith("api."):
            # Return JSONified error if a request is made to the REST API.
            return InvalidUsage(str(error), status_code=error.code).to_dict(), error.code
        return route(error)

    return wrapper


@errors.app_errorhandler(400)
@api_error_reroute
def error_400(error):
    """Error: Bad Request"""


@errors.app_errorhandler(403)
@api_error_reroute
def error_403(error):
    """Error: Forbidden"""
    content = {
        "title": "Error 403",
        "profile_img": "trevor.jpeg",
    }
    return render_template("errors/403.html", content=content), 403


@errors.app_errorhandler(404)
@api_error_reroute
def error_404(error):
    """Error: Page Not Found"""
    content = {
        "title": "Error 404",
        "profile_img": "feynman.jpeg",
    }
    return render_template("errors/404.html", content=content), 404


@errors.app_errorhandler(429)
@api_error_reroute
def error_429(error):
    """Error: Too Many Requests"""
    content = {
        "title": "Error 429",
        "profile_img": "trevor.jpeg",
    }
    return render_template("errors/429.html", content=content), 429


@errors.app_errorhandler(500)
@api_error_reroute
def error_500(error):
    """Error: Internal Server Error"""
    content = {
        "title": "Error 500",
        "profile_img": "cory.jpeg",
    }
    return render_template("errors/500.html", content=content), 500
