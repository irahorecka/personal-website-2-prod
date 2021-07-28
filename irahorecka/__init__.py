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

db = SQLAlchemy()


def create_app(config_class=Config):
    """Creates Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    from irahorecka.main.routes import main
    from irahorecka.housing.routes import housing
    from irahorecka.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(housing)
    app.register_blueprint(errors)

    return app
