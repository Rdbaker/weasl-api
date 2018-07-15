# -*- coding: utf-8 -*-
"""Error codes for use in the application."""


class Errors(object):
    """Contansts for errors in the form of: (code, message)."""

    BAD_GUID = ('bad-guid', 'We couldn\'t understand the format of the ID.')
    NO_TOKEN = ('missing-token', 'Missing authentication token.')
    BAD_TOKEN = ('bad-token', 'Invalid or expired token.')
    PHONE_REQUIRED = ('phone-number-required', 'Phone number is required')
    EMAIL_REQUIRED = ('email-required', 'Email is required')
    LOGIN_REQUIRED = ('login-required', 'Login required for that')
