"""
/wsgi.py
~~~~~~~~

WSGI entry point to start a Flask web application instance.
"""

from irahorecka import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
