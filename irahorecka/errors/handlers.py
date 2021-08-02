"""
/irahorecka/errors/handlers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask blueprint to handle errors.
"""

from flask import request, render_template, Blueprint

from irahorecka.exceptions import InvalidUsage

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def error_404(error):
    """Error: Page not found"""
    # Return jsonified error response if request was made via domain pattern api.irahorecka.com/*
    if request.headers["Host"].startswith("api"):
        return InvalidUsage(str(error), status_code=404).to_dict(), 404
    content = {
        "title": "Error 404",
        "profile_img": "feynman.jpeg",
    }
    return render_template("errors/404.html", content=content), 404


@errors.app_errorhandler(403)
def error_403(error):
    """Error: Forbidden"""
    if request.headers["Host"].startswith("api"):
        return InvalidUsage(str(error), status_code=403).to_dict(), 403
    content = {
        "title": "Error 403",
        "profile_img": "trevor.jpeg",
    }
    return render_template("errors/403.html", content=content), 403


@errors.app_errorhandler(500)
def error_500(error):
    """Error: Internal Server Error"""
    if request.headers["Host"].startswith("api"):
        return InvalidUsage(str(error), status_code=500).to_dict(), 500
    content = {
        "title": "Error 500",
        "profile_img": "cory.jpeg",
    }
    return render_template("errors/500.html", content=content), 500
