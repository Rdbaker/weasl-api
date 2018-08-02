import datetime as dt
import random
import enum
import uuid

import boto3
import jwt
import pytz
from flask import current_app
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint

from weasl.constants import Errors
from weasl.database import (Column, Model, db, reference_col,
                            IDModel, relationship)
from weasl.errors import Unauthorized

class OrgPropertyNamespaces(enum.Enum):
    NONE = '*'
    GATES = 'gates'
    THEME = 'theme'
    SETTINGS = 'settings'


class OrgProperty():
    org_id = reference_col('orgs', primary_key=True)
    property_name = Column(db.String(255), primary_key=True)
    property_value = Column(db.String(255))
    property_type = Column(db.String(90), nullable=False)
    property_namespace = Column(db.Enum(OrgPropertyNamespaces))


class Org(IDModel):
    """A class for orgs in the database."""

    __tablename__ = 'orgs'

    client_id = Column(db.String(255), default=lambda _: uuid.uuid4().hex[:10], index=True, unique=True)
    client_secret = Column(db.String(255), default=lambda _: uuid.uuid4().hex, index=True, unique=True)

    @classmethod
    def generate_new(cls):
        """Generate a new org."""
        unused_id = uuid.uuid4().hex[:10]
        maybe_org = cls.from_client_id(unused_id)
        while maybe_org is not None:
            unused_id = uuid.uuid4().hex[:10]
            maybe_org = cls.from_client_id(unused_id)
        unused_secret = uuid.uuid4().hex
        maybe_org = cls.from_client_secret(unused_secret)
        while maybe_org is not None:
            unused_secret = uuid.uuid4().hex
            maybe_org = cls.from_client_secret(unused_secret)
        return Org.create(client_id=unused_id, client_secret=unused_secret)

    @classmethod
    def from_client_id(cls, maybe_id):
        """Get the org from the client ID."""
        org = Org.query.filter(Org.client_id == maybe_id).first()
        return org

    @classmethod
    def from_client_secret(cls, maybe_secret):
        """Get the org from the client secret."""
        org = Org.query.filter(Org.client_secret == maybe_secret).first()
        return org