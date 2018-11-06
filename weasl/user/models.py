import datetime as dt
import random
import uuid

import boto3
import jwt
import pytz
from flask import current_app, render_template
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint

from weasl.constants import Errors
from weasl.database import (Column, Model, UUIDModel, db, reference_col,
                             relationship)
from weasl.errors import Unauthorized


class EmailToken(Model):
    """A class for an email token."""

    __tablename__ = 'users_email_auth_token'

    token = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    user_id = reference_col('users', primary_key=True)
    user = relationship('User')
    created_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    expired_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    active = Column(db.Boolean, default=False, index=True)
    sent = Column(db.Boolean, default=False, index=True)

    @classmethod
    def generate(cls, user):
        """Create a random email token."""
        token = uuid.uuid4()
        email_token = cls.query.filter(cls.token == token)
        while email_token is not None:
            token = uuid.uuid4()
            email_token = cls.query.filter(cls.token == token).first()
        return cls.create(
            token=token,
            user_id=user.id,
            active=True,
            sent=False,
            expired_at=dt.datetime.utcnow() + dt.timedelta(hours=12)
        )

    @classmethod
    def use(cls, token):
        """Use the token to authenticate the user."""
        email_token = cls.query.filter(
            cls.token == token,
            cls.active == True,
            cls.expired_at > dt.datetime.utcnow().replace(tzinfo=pytz.utc),
        ).first()

        if email_token:
            email_token.update(active=False)
        return email_token

    def send(self):
        """Send the token to the user."""
        if current_app.config.get('SEND_EMAILS'):
            email = self.user.email
            ses_client = boto3.client('ses', region_name='us-west-2')
            ses_client.send_email(
                Source=current_app.config['FROM_EMAIL'],
                Destination={
                    'ToAddresses': [email],
                },
                Message={
                    'Subject': {
                        'Data': 'Log in to your Weasl account'
                    },
                    'Body': {
                        'Html': {
                            'Data': render_template(
                                'emails/magiclink.html',
                                org_name='Weasl',
                                email_magiclink='{}/magiclink/{}'.format(current_app.config.get('BASE_SITE_HOST'), self.token)
                            )
                        }
                    }
                }
            )
        self.update(sent=True)


class SMSToken(Model):
    """A class for SMS authentication tokens."""

    __tablename__ = 'users_sms_auth_token'

    TOKEN_CHARACTERS = '0123456789abcdefghijklmonpqrstuvwxyz'

    token = Column(db.String(6), primary_key=True)
    user_id = reference_col('users', primary_key=True)
    user = relationship('User')
    created_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    expired_at = Column(db.DateTime(timezone=True), nullable=False,
                        default=dt.datetime.utcnow)
    active = Column(db.Boolean, default=False, index=True)
    sent = Column(db.Boolean, default=False, index=True)

    @staticmethod
    def create_random_token():
        """Create a random 6-digit token."""
        return ''.join([random.choice(SMSToken.TOKEN_CHARACTERS) for _ in range(6)])

    @classmethod
    def generate(cls, user):
        """Create a new SMS Token for a given user."""
        text_token = cls.create_random_token()
        sms_token = cls.query.filter(cls.token == text_token).first()
        while sms_token is not None:
            text_token = cls.create_random_token()
            sms_token = cls.query.filter(cls.token == text_token).first()
        return cls.create(
            token=text_token,
            user_id=user.id,
            active=True,
            sent=False,
            expired_at=dt.datetime.utcnow() + dt.timedelta(hours=1)
        )

    @classmethod
    def use(cls, token_string: str):
        """Use the token to authenticate the user."""
        sms_token = cls.query.filter(
            cls.token == token_string.lower(),
            cls.active == True,
            cls.expired_at > dt.datetime.utcnow().replace(tzinfo=pytz.utc),
        ).first()
        if sms_token:
            sms_token.update(active=False)
        return sms_token

    def send(self):
        """Send the token to the user."""
        if current_app.config.get('SEND_SMS'):
            phone_number = self.user.phone_number
            current_app.twilio_client.messages.create(
                to=phone_number,
                from_=current_app.config['TWILIO_FROM_NUMBER'],
                body='Use this code to login to Weasl: {}'.format(self.token)
            )
        self.update(sent=True)


class User(UUIDModel):
    """A class for users in the database."""

    __tablename__ = 'users'

    is_admin = Column(db.Boolean, default=False)
    email = Column(db.String(90), index=True, nullable=True, unique=True)
    phone_number = Column(db.String(50), index=True, nullable=True, unique=True)
    org_id = reference_col('orgs', nullable=False)
    # ALL TIME ARE IN UTC
    created_at = Column(db.DateTime(timezone=True), nullable=True,
                        default=dt.datetime.utcnow)
    last_login_at = Column(db.DateTime(timezone=True), nullable=True,
                           default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime(timezone=True), nullable=True,
                        default=dt.datetime.utcnow)


    @classmethod
    def from_token(cls, token: str):
        """Get the user from an auth token."""
        user_id = User.decode_auth_token(token)
        if user_id:
            return User.find(user_id)

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
