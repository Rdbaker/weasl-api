# -*- coding: utf-8 -*-
"""Factories to help in tests."""
import random

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from weasl.database import db
from weasl.user.models import User
from weasl.end_user.models import EndUser
from weasl.org.models import Org, OrgProperty


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
    phone_number = Sequence(lambda n: '+1' + ''.join([str(random.randint(0, 9)) for _ in range(10)]))

    class Meta:
        """Factory configuration."""

        model = User

class EndUserFactory(BaseFactory):
    """EndUser factory."""

    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
    phone_number = Sequence(lambda n: '+1' + ''.join([str(random.randint(0, 9)) for _ in range(10)]))

    class Meta:
        """Factory configuration."""

        model = EndUser


class OrgFactory(BaseFactory):
    """Org factory."""

    class Meta:
        """Factory configuration."""

        model = Org

class OrgPropFactory(BaseFactory):
    """Org property factory."""

    class Meta:
        """Factory configuration."""

        model = OrgProperty