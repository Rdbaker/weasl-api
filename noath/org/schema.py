# -*- coding: utf-8 -*-
"""Org schema."""
from marshmallow import Schema, fields, ValidationError, validate


class OrgSchema(Schema):
    """A schema for an Org model."""

    id = fields.Int(dump_only=True)
    api_key = fields.String()

    class Meta:
        """Meta class for the Org schema."""

        type_ = 'org'
        strict = True
