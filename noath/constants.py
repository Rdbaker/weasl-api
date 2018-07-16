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
    API_KEY_REQUIRED = ('api-key-required', 'An API key is required for that')
    END_USER_MISSING_IDENTIFIER = ('missing-identifier', 'Email or phone number required to create a user.')
    END_USER_DUPLICATE_EMAIL = ('duplicate-email', 'A user with that email already exists.')
    END_USER_DUPLICATE_PHONE = ('duplicate-phone', 'A user with that phone number already exists.')

class Success(object):
    """Constants for success in the form of: (code, message)."""

    END_USER_CREATED = ('end-user-created', 'End user was created successfully')
