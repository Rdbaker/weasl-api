# -*- coding: utf-8 -*-
"""User schema."""
from marshmallow import Schema, fields


class UserSchema(Schema):
    """A schema for a User model."""

    id = fields.UUID(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    email = fields.String()
    phone_number = fields.String()
    org_id = fields.Int()

    private_fields = ['email', 'phone_number']

    class Meta:
        """Meta class for User schema."""

        type_ = 'user'
        strict = True
