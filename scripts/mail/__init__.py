"""
/scripts/mail/__init__.py

Concerns all things emails.
"""

import os
from functools import partial

from dotenv import load_dotenv

from scripts.mail.mail import write_email

load_dotenv()
write_email = partial(write_email, os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
