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
    org_id = reference_col('orgs')
    property_name = Column(db.String(255), index=True, nullable=False)
    property_value = Column(db.String(255), index=True, nullable=False)
    property_type = Column(db.String(90), nullable=False)


class Org(IDModel):
    """A class for orgs in the database."""

    __tablename__ = 'orgs'

    api_key = Column(db.String(255), default=lambda _: uuid.uuid4().hex)
