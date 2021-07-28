"""
/enrichment/__init__.py
Ira Horecka - June 2021
~~~~~~~~~~~~~~~~~~~~~~~

#
"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from irahorecka.config import Config

application = Flask(__name__)
db = SQLAlchemy()


def create_app(config_class=Config):
    """Creates Flask application instance."""
    application.config.from_object(Config)
    CORS(application)
    db.init_app(application)

    from irahorecka.main.routes import main
    from irahorecka.housing.routes import housing
    from irahorecka.errors.handlers import errors

    application.register_blueprint(main)
    application.register_blueprint(housing)
    application.register_blueprint(errors)

    return application
