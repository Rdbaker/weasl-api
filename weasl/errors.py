# -*- coding: utf-8 -*-
"""A file for all the error classes."""


class APIException(Exception):
    """A class to be inherited from for other API exceptions."""

    status_code = 400

    def __init__(self, error_locale, status_code=None):
        """Create a new error from a given error locale.
        :param error_locale tuple: tuple of (code, message), likely from the
            locales.Errors class
        :param status_code int: (default: None) you'll most likely declare this
            on the class instead of at init time.
        """
        self.error_code = error_locale[0]
        self.error_message = error_locale[1]
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        """Return a dict form of the error."""
        return {
            'error_code': self.error_code,
            'error_message': self.error_message
        }


class BadRequest(APIException):
    """A plain old 400."""


class Unauthorized(APIException):
    """A 401 code."""

    status_code = 401


class Forbidden(APIException):
    """APIException for a 403."""

    status_code = 403


class NotFound(APIException):
    """APIException for a 404."""

    status_code = 404


class ProxyAuthenticationRequired(APIException):
    """APIException for a 407."""

    status_code = 407


class Conflict(APIException):
    """A 409 code."""

    status_code = 409


class UnprocessableEntity(APIException):
    """A 422 code."""

    status_code = 422


class PreconditionRequired(APIException):
    """A 428 code."""

    status_code = 428


class InternalServerError(APIException):
    """A 500 code."""

    status_code = 500
