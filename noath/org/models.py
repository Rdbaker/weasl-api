import datetime as dt
import random
import uuid

import boto3
import jwt
import pytz
from flask import current_app
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint

from noath.constants import Errors
from noath.database import (Column, Model, db, reference_col,
                            IDModel, relationship)
from noath.errors import Unauthorized

class OrgProperty():
    org_id = reference_col('orgs', primary_key=True)
    property_name = Column(db.String(255), primary_key=True)
    property_value = Column(db.String(255))
    property_type = Column(db.String(90), nullable=False)


class Org(IDModel):
    """A class for orgs in the database."""

    __tablename__ = 'orgs'

    api_key = Column(db.String(255), default=lambda _: uuid.uuid4().hex, index=True)

    @classmethod
    def from_api_key(cls, maybe_key):
        """Get the org from the API key."""
        org = Org.query.filter(Org.api_key == maybe_key).first()
        return org