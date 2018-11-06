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
    INVALID_CLIENT_ID = ('invalid-client-id', 'The client ID is invalid')
    CLIENT_ID_REQUIRED = ('client-id-required', 'A client ID is required for that action')
    CLIENT_SECRET_REQUIRED = ('client-secret-required', 'A client secret is required for that action')
    INVALID_CLIENT_SECRET = ('invalid-client-secret', 'The client secret is invalid')
    END_USER_NOT_FOUND = ('end-user-not-found', 'That end user does not exist')
    ATTRIBUTE_VALUE_MISSING = ('attributes-value-missing', 'A value is required for the attribute')
    ATTRIBUTE_TYPE_MISSING = ('attributes-type-missing', 'A type is required for the attribute')
    BAD_PROPERTY_TYPE = ('bad-property-type', 'Property type must be one of: STRING, NUMBER, JSON, BOOLEAN')

class Success(object):
    """Constants for success in the form of: (code, message)."""

    END_USER_CREATED = ('end-user-created', 'End user was created successfully')
