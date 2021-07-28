from flask import render_template, Blueprint

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def error_404(error):
    """Error: Page not found"""
    content = {
        "title": "Error 404",
        "profile_img": "feynman.jpeg",
    }
    return render_template("errors/404.html", content=content), 404


@errors.app_errorhandler(403)
def error_403(error):
    """Error: Forbidden"""
    content = {
        "title": "Error 403",
        "profile_img": "trevor.jpeg",
    }
    return render_template("errors/403.html", content=content), 403


@errors.app_errorhandler(500)
def error_500(error):
    """Error: Internal Server Error"""
    content = {
        "title": "Error 500",
        "profile_img": "cory.jpeg",
    }
    return render_template("errors/500.html", content=content), 500
