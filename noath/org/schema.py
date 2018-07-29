# -*- coding: utf-8 -*-
"""Org schema."""
from marshmallow import Schema, fields, ValidationError, validate


class OrgSchema(Schema):
    """A schema for an Org model."""

    id = fields.Int(dump_only=True)
    client_id = fields.String()
    client_secret = fields.String()

    class Meta:
        """Meta class for the Org schema."""

        type_ = 'org'
        strict = True
