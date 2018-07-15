# -*- coding: utf-8 -*-
"""Factories to help in tests."""
import random

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from noath.database import db
from noath.user.models import User
from noath.org.models import Org


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

class OrgFactory(BaseFactory):
    """Org factory."""

    class Meta:
        """Factory configuration."""

        model = Org