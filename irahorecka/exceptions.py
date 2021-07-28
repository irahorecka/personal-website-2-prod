"""
"""


class InvalidUsage(Exception):
    """Returns JSON response outlining invalid usage status and message."""

    status_code = 400
    status_text = "BAD_REQUEST"

    def __init__(self, message, status_code=None, status_text=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if status_text is not None:
            self.status_text = status_text
        self.payload = payload

    def to_dict(self):
        """Converts payload to dict - also adds 'status' and 'message' attributes."""
        rv = dict(self.payload or ())
        rv["status"] = self.status_text
        rv["message"] = self.message
        return rv


class ValidationError(Exception):
    """Validation of request args failed."""

    pass
