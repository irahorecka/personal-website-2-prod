"""
/irahorecka/__init__.py

Concerns all things irahorecka.com.
"""

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

from irahorecka.config import Config

application = Flask(__name__)
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)


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
    # Housing widget makes multiple requests when lazy loading table contents. Increase limit.
    limiter.limit("1000/day")(housing)
    application.register_blueprint(main)
    application.register_blueprint(housing)
    application.register_blueprint(errors)

    return application
