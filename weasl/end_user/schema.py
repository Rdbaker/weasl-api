# -*- coding: utf-8 -*-
"""User schema."""
from marshmallow import Schema, fields, ValidationError, validates_schema

from weasl.constants import Errors


class EndUserSchema(Schema):
    """A schema for an EndUser model."""

    id = fields.UUID(dump_only=True)
    email = fields.String()
    phone_number = fields.String()
    last_login_at = fields.DateTime()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    attributes = fields.Raw()

    private_fields = ['email', 'phone_number']

    class Meta:
        """Meta class for the EndUser schema."""

        type_ = 'end_user'
        strict = True

    @validates_schema
    def validate_end_user(self, data):
        """Validate the end_user."""
        # TODO: more validation
        if data.get('email') is None and data.get('phone_number') is None:
            raise ValidationError(Errors.END_USER_MISSING_IDENTIFIER[1])