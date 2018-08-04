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


class OrgPropertyTypes(enum.Enum):
    STRING = 'str'
    NUMBER = 'int'
    JSON = 'json.loads'
    BOOLEAN = 'bool'


class OrgProperty(Model):
    """A class for org properties in the database."""

    __tablename__ = 'org_properties'

    org_id = reference_col('orgs', primary_key=True)
    property_name = Column(db.String(511), primary_key=True)
    property_value = Column(db.Text())
    property_type = Column(db.Enum(OrgPropertyTypes), nullable=False)
    property_namespace = Column(db.Enum(OrgPropertyNamespaces))

    @classmethod
    def get_by_org(cls, org_id):
        """Get all the properties for the org."""
        return cls.query.filter(cls.org_id == org_id).all()


class Org(IDModel):
    """A class for orgs in the database."""

    __tablename__ = 'orgs'

    client_id = Column(db.String(255), default=lambda _: uuid.uuid4().hex[:10], index=True, unique=True, nullable=False)
    client_secret = Column(db.String(255), default=lambda _: uuid.uuid4().hex, index=True, unique=True, nullable=False)

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

    @property
    def properties(self):
        """Get all the properties for the org."""
        return OrgProperty.get_by_org(self.id)

    @classmethod
    def from_client_secret(cls, maybe_secret):
        """Get the org from the client secret."""
        org = Org.query.filter(Org.client_secret == maybe_secret).first()
        return org