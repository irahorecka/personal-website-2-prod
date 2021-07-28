from irahorecka import db


def setup(app):
    with app.app_context():
        db.create_all()
