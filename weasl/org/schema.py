# -*- coding: utf-8 -*-
"""Org schema."""
import json
from marshmallow import Schema, fields, ValidationError, validate

from weasl.org.models import OrgPropertyTypes


class OrgPropertySchema(Schema):
    """A schema for an Org Property model."""

    property_name = fields.Str(dump_to='name')
    value = fields.Method('derive_value')

    class Meta:
        """Meta class for org property."""

        type_ = 'org_property'
        strict = True

    def derive_value(self, prop):
        """derive the value for the property."""
        converter = eval('{}'.format(prop.property_type.value))
        return converter(prop.property_value)


class OrgSchema(Schema):
    """A schema for an Org model."""

    id = fields.Int(dump_only=True)
    client_id = fields.String()
    client_secret = fields.String()
    properties = fields.Nested('OrgPropertySchema',
                               dump_only=True,
                               many=True,
                               exclude=('org_id',))

    class Meta:
        """Meta class for the Org schema."""

        type_ = 'org'
        strict = True
