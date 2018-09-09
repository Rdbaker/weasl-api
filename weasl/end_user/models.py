import datetime as dt
import random
import uuid
import urllib.parse as urlparse
from urllib.parse import urlencode

import boto3
import jwt
import pytz
from flask import current_app, render_template
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.schema import UniqueConstraint

from weasl.org.models import OrgProperty
from weasl.org.constants import OrgPropertyConstants
from weasl.constants import Errors
from weasl.database import (Column, Model, UUIDModel, db, reference_col,
                             relationship)
from weasl.errors import Unauthorized


class EmailToken(Model):
    """A class for an email token."""

    __tablename__ = 'end_users_email_auth_token'

    token = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    end_user_id = reference_col('end_users', primary_key=True)
    end_user = relationship('EndUser')
    created_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    expired_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    active = Column(db.Boolean, default=False, index=True)
    sent = Column(db.Boolean, default=False, index=True)
    org_id = reference_col('orgs', index=True, nullable=True)

    @classmethod
    def generate(cls, end_user):
        """Create a random email token."""
        token = uuid.uuid4()
        email_token = cls.query.filter(cls.token == token)
        while email_token is not None:
            token = uuid.uuid4()
            email_token = cls.query.filter(cls.token == token).first()
        return cls.create(
            token=token,
            end_user_id=end_user.id,
            active=True,
            sent=False,
            expired_at=dt.datetime.utcnow() + dt.timedelta(hours=12)
        )

    @classmethod
    def use(cls, token):
        """Use the token to authenticate the end_user."""
        email_token = cls.query.filter(
            cls.token == token,
            cls.active == True,
            cls.expired_at > dt.datetime.utcnow().replace(tzinfo=pytz.utc),
        ).first()

        if email_token:
            email_token.update(active=False)
        return email_token

    def make_magiclink(self):
        """Make the magiclink for the token, preserving the query params in the org's email."""
        custom_url = OrgProperty.find_for_org(self.org_id, OrgPropertyConstants.EMAIL_MAGICLINK)
        url = (custom_url.property_value if current_url else current_app.config.get('BASE_SITE_HOST'))
        params = { 'w_token': self.token }

        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)

        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)

    def send(self):
        """Send the token to the end_user."""
        if current_app.config.get('SEND_EMAILS'):
            email = self.end_user.email
            ses_client = boto3.client('ses', region_name='us-west-2')
            org_name = OrgProperty.find_for_org(self.org_id, OrgPropertyConstants.COMPANY_NAME)
            ses_client.send_email(
                Source=current_app.config['FROM_EMAIL'],
                Destination={
                    'ToAddresses': [email],
                },
                ConfigurationSetName='suetco',
                Message={
                    'Subject': {
                        'Data': 'Log in to your {} account'.format(org_name.property_value if org_name else '')
                    },
                    'Body': {
                        'Html': {
                            'Data': render_template(
                                'emails/magiclink.html',
                                org_name=org_name.property_value if org_name else '',
                                email_magiclink='{}'.format(self.make_magiclink())
                            )
                        }
                    }
                }
            )
        self.update(sent=True)




class SMSToken(Model):
    """A class for SMS authentication tokens."""

    __tablename__ = 'end_users_sms_auth_token'

    TOKEN_CHARACTERS = '0123456789abcdefghijklmonpqrstuvwxyz'

    token = Column(db.String(6), primary_key=True)
    end_user_id = reference_col('end_users', primary_key=True)
    end_user = relationship('EndUser')
    created_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    expired_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    active = Column(db.Boolean, default=False, index=True)
    sent = Column(db.Boolean, default=False, index=True)
    org_id = reference_col('orgs', index=True, nullable=True)

    @staticmethod
    def create_random_token():
        """Create a random 6-digit token."""
        return ''.join([random.choice(SMSToken.TOKEN_CHARACTERS) for _ in range(6)])

    @classmethod
    def generate(cls, end_user):
        """Create a new SMS Token for a given end_user."""
        text_token = cls.create_random_token()
        sms_token = cls.query.filter(cls.token == text_token).first()
        while sms_token is not None:
            text_token = cls.create_random_token()
            sms_token = cls.query.filter(cls.token == text_token).first()
        return cls.create(
            token=text_token,
            end_user_id=end_user.id,
            active=True,
            sent=False,
            expired_at=dt.datetime.utcnow() + dt.timedelta(hours=1),
        )

    @classmethod
    def use(cls, token_string: str):
        """Use the token to authenticate the end_user."""
        sms_token = cls.query.filter(
            cls.token == token_string.lower(),
            cls.active == True,
            cls.expired_at > dt.datetime.utcnow().replace(tzinfo=pytz.utc),
        ).first()
        if sms_token:
            sms_token.update(active=False)
        return sms_token

    def send(self):
        """Send the token to the end_user."""
        if current_app.config.get('SEND_SMS'):
            phone_number = self.end_user.phone_number
            current_app.twilio_client.messages.create(
                to=phone_number,
                from_=current_app.config['TWILIO_FROM_NUMBER'],
                body='{}: {}'.format(
                    OrgProperty.get_for_org_with_default(self.end_user.org_id, OrgPropertyConstants.TEXT_LOGIN_MESSAGE),
                    self.token,
                )
            )
        self.update(sent=True)


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()


class EndUser(UUIDModel):
    """A class for end_users in the database."""

    __tablename__ = 'end_users'

    attributes = Column(MutableDict.as_mutable(JSONB()))
    email = Column(db.String(90), index=True, nullable=True)
    phone_number = Column(db.String(50), index=True, nullable=True)
    org_id = reference_col('orgs', nullable=False, index=True)
    # ALL TIME ARE IN UTC
    created_at = Column(db.DateTime(timezone=True), nullable=True,
                        default=dt.datetime.utcnow)
    last_login_at = Column(db.DateTime(timezone=True), nullable=True,
                           default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime(timezone=True), nullable=True,
                        default=dt.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('org_id', 'email', name='_email_org_uc'),
        UniqueConstraint('org_id', 'phone_number', name='_phone_org_uc'),
    )

    @classmethod
    def from_token(cls, token: str):
        """Get the end_user from an auth token."""
        end_user_id = EndUser.decode_auth_token(token)
        if end_user_id:
            return EndUser.find(end_user_id)

    @staticmethod
    def decode_auth_token(auth_token: str) -> str:
        """
        Decodes the auth token
        :param str auth_token:
        :return: string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise Unauthorized(Errors.BAD_TOKEN)

    def encode_auth_token(self) -> str:
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': dt.datetime.utcnow() + dt.timedelta(days=7),
                'iat': dt.datetime.utcnow(),
                'sub': str(self.id),
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e
