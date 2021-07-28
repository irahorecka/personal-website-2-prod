import os
from functools import partial

from scripts.mail.mail import write_email

write_email = partial(write_email, os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
