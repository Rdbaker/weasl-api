# -*- coding: utf-8 -*-
"""Database module, including the database object and DB-related utilities."""
import uuid

from sqlalchemy.dialects.postgresql import UUID

from .constants import Errors
from .errors import BadRequest
from .extensions import db

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class PersistentMixin(CRUDMixin):
    r"""Mixin that doesn't let a model be deleted from the database. Doesn't \
    allow for very transparent reads, either."""

    # TODO: make a better pattern for this. One that goes lower under
    # SQLAlchemy's abstraction layers
    __table_args__ = {'extend_existing': True}

    _deleted = db.Column(db.Boolean, index=True, default=False)

    @classmethod
    def get(cls, pk):
        """Get without retreiving deleted."""
        inst = super()
        if inst is not None and inst._deleted is True:
            return None
        return inst

    def delete(self, *args, **kwargs):
        """Don't actually delete, just set _deleted to True."""
        self.update(_deleted=True)
        return None


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    r"""A mixin that adds a surrogate integer 'primary key' column named ``id`` \
    to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, (str, bytes)) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))
        return None

    @classmethod
    def find(cls, record_id):
        """Alias for get_by_id."""
        return cls.get_by_id(record_id)


class UUIDMixin(object):
    """A mixin that is like SurrogatePK mixin, but uses PostgreSQL's UUID type
    instead of an integer ID."""
    __table_args = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), nullable=False, primary_key=True,
                default=uuid.uuid4)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by UUID."""
        if not isinstance(record_id, uuid.UUID):
            try:
                record_id = uuid.UUID(record_id)
            except:
                raise BadRequest(Errors.BAD_GUID)
        return cls.query.get(record_id)

    @classmethod
    def find(cls, record_id):
        """Alias for get_by_id."""
        return cls.get_by_id(record_id)


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class UUIDModel(Model, UUIDMixin):
    __abstract__ = True


class IDModel(Model, SurrogatePK):
    __abstract__ = True
