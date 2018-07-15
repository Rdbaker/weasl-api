# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import pytest
from webtest import TestApp

from noath.app import create_app
from noath.database import db as _db
from noath.settings import TestConfig

from .factories import UserFactory, OrgFactory


@pytest.yield_fixture(scope='function')
def app():
    """An application for the tests."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def org(db):
    """An org factory for the tests."""
    org = OrgFactory()
    db.session.commit()
    return org


@pytest.fixture
def user(db, org):
    """A user for the tests."""
    user = UserFactory(org_id=org.id)
    db.session.commit()
    return user
