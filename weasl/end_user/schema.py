# -*- coding: utf-8 -*-
"""User schema."""
from marshmallow import Schema, fields, ValidationError, validates_schema

from weasl.constants import Errors


class EndUserSchema(Schema):
    """A schema for an EndUser model."""

    id = fields.UUID(dump_only=True)
    email = fields.String(load_only=True)
    phone_number = fields.String(load_only=True)
    identity = fields.Method('derive_identity', dump_only=True)
    activity = fields.Method('derive_activity', dump_only=True)
    attributes = fields.Raw()

    private_fields = ['identity']

    class Meta:
        """Meta class for the EndUser schema."""

        type_ = 'end_user'
        strict = True

    def derive_activity(self, end_user):
        return {
            'created_at': end_user.created_at,
            'updated_at': end_user.updated_at,
            'last_login_at': end_user.last_login_at,
        }

    def derive_identity(self, end_user):
        return {
            'email': end_user.email,
            'phone_number': end_user.phone_number,
        }

    @validates_schema
    def validate_end_user(self, data):
        """Validate the end_user."""
        # TODO: more validation
        if data.get('email') is None and data.get('phone_number') is None:
            raise ValidationError(Errors.END_USER_MISSING_IDENTIFIER[1])