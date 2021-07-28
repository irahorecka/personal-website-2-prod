"""
/run.py
Ira Horecka - July 2021
~~~~~~~~~~~~~~~~~~~~~~~

Starts a Flask web application instance.
"""

from irahorecka import create_app

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0")
