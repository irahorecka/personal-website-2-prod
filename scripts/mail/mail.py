"""
/scripts/mail/mail.py
~~~~~~~~~~~~~~~~~~~~~

Module for sending emails via Gmail.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def write_email(sender_email, sender_pass, recipient_email, subject, body, code=""):
    """ENTRY POINT: Constructs email sender, recipients, and content."""
    # Add new posts to Email object in text and markup format.
    content = f"""
        Message: {body}
        Code: {code}
        """
    html_content = f"""
        <p>{body}</p>
        <code>{code}</code>"""
    mail = Email(content, html_content)

    # Add Email metadata.
    metadata = EmailMetadata()
    metadata.sender_email = sender_email
    metadata.sender_password = sender_pass
    metadata.recipient_email = recipient_email
    metadata.subject = subject
    metadata.construct_MIME()

    try:
        # Attempt to send email to user if new posts found.
        text, html = mail.get_markup()
        # Make sure no empty str returned.
        if text:
            send_email(metadata, text, html)
    except AttributeError:
        # Markup returned None.
        pass


class EmailMetadata:
    """Constructor for email metadata."""

    def __init__(self):
        self.sender_email = ""
        self.sender_password = ""
        self.recipient_email = ""
        self.subject = ""
        self.message = ""

    def construct_MIME(self):
        """Constructs MIMEMultipart object from instance attributes."""
        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = self.subject
        self.message["From"] = self.sender_email
        self.message["To"] = self.recipient_email


class Email:
    """Constructor for email body."""

    def __init__(self, content, html_content=""):
        self.text_body = content
        self.html_body = html_content

    def get_markup(self):
        """Concatenates self.text_body and self.html_body in markup format for email."""
        text_markup = f"""\
            {self.text_body}
        """
        html_markup = f"""\
            <html>
            <body>
                <p>
                {self.html_body}
                </p>
            </body>
            </html>
        """

        return text_markup, html_markup


def send_email(metadata, text, html):
    """Builds and sends email from Gmail account."""
    text_mail = MIMEText(text, "plain")
    html_mail = MIMEText(html, "html")
    message = metadata.message

    # Attach both text and html versions of email.
    message.attach(text_mail)
    message.attach(html_mail)

    ssl_context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as server:
        server.login(metadata.sender_email, metadata.sender_password)
        server.sendmail(metadata.sender_email, metadata.recipient_email, message.as_string())
