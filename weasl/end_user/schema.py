# -*- coding: utf-8 -*-
"""User schema."""
from marshmallow import Schema, fields, ValidationError, validates_schema

from weasl.constants import Errors
from weasl.end_user.models import EndUserPropertyTypes

class EndUserSchema(Schema):
    """A schema for an EndUser model."""

    id = fields.UUID(dump_only=True)
    email = fields.String(load_only=True)
    phone_number = fields.String(load_only=True)
    identity = fields.Method('derive_identity', dump_only=True)
    activity = fields.Method('derive_activity', dump_only=True)
    attributes = fields.Method('attributes_from_properties', dump_only=True)

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
            'is_first_login': end_user.last_login_at is None,
        }

    def derive_identity(self, end_user):
        return {
            'email': end_user.email,
            'phone_number': end_user.phone_number,
        }

    def attributes_from_properties(self, end_user):
        attrs = {}
        for prop in end_user.properties:
            converter = eval('{}'.format(prop.property_type.value))
            attrs[prop.property_name] = {
                'value': converter(prop.property_value),
                'trusted': prop.trusted,
            }
        return attrs

    @validates_schema
    def validate_end_user(self, data):
        """Validate the end_user."""
        # TODO: more validation
        if data.get('email') is None and data.get('phone_number') is None:
            raise ValidationError(Errors.END_USER_MISSING_IDENTIFIER[1])