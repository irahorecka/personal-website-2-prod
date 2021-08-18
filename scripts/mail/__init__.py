"""
/scripts/mail/__init__.py

Concerns all things emails.
"""

import inspect
import os
import traceback

from dotenv import load_dotenv

from scripts.mail.mail import write_email

load_dotenv()


def email_if_exception(func):
    """Wrapper that sends an email to ira.horecka@yahoo.com if the
    wrapped function raises an exception."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            write_email(
                os.environ["EMAIL_USER"],
                os.environ["EMAIL_PASS"],
                "ira.horecka@yahoo.com",
                f"An exception occurred in function {inspect.getfile(func)}::{func.__name__}",
                f"An exception occurred in function {inspect.getfile(func)}::{func.__name__}. Check error message below.",
                code=str(traceback.format_exc()),
            )

    return wrapper
