"""
/irahorecka/__init__.py

Concerns all things irahorecka.com.
"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from irahorecka.config import Config
from irahorecka.core import limiter

application = Flask(__name__)
db = SQLAlchemy()


def create_app(config_class=Config):
    """Creates Flask application instance."""
    application.config.from_object(config_class)
    CORS(application)
    db.init_app(application)

    from irahorecka.main.routes import main
    from irahorecka.housing.routes import housing
    from irahorecka.errors.handlers import errors

    limiter.init_app(application)
    limiter.limit("200/day")(main)
    limiter.limit("200/day")(housing)
    application.register_blueprint(main)
    application.register_blueprint(housing)
    application.register_blueprint(errors)

    return application
