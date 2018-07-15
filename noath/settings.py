# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    TESTING = False
    SECRET_KEY = os.environ.get('NOATH_SECRET', 'secret-key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_API_HOST = 'http://localhost:5000'
    SEND_EMAILS = True
    SEND_SMS = True

    # Twilio stuff
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')

    # email stuff
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@noath.org')


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    BASE_API_HOST = 'https://api.noath.org'


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres://noath:noath123@' + \
        'localhost:5432/noath'


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SEND_EMAILS = False
    SEND_SMS = False
    SQLALCHEMY_DATABASE_URI = 'postgres://noath:noath123@' + \
        'localhost:5432/noath_test'
