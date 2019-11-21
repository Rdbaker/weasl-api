# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import pytest
from webtest import TestApp

from weasl.app import create_app
from weasl.database import db as _db
from weasl.settings import TestConfig
from weasl.end_user.models import EndUserPropertyTypes

from .factories import OrgFactory, EndUserFactory, EndUserPropFactory


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
def end_user(db, org):
    """An end user for the tests."""
    end_user = EndUserFactory(org_id=org.id)
    db.session.commit()
    return end_user


@pytest.fixture
def end_user_as_weasl_user(db, org):
    """An end user as a weasl user for the tests."""
    end_user = EndUserFactory(org_id=org.id)
    db.session.commit()
    EndUserPropFactory(
        end_user_id=end_user.id,
        property_name='org_id_as_admin',
        property_value=str(org.id),
        property_type=EndUserPropertyTypes.NUMBER,
        trusted=True,
    )
    db.session.commit()
    return end_user
