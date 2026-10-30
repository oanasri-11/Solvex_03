"""Shared SQLAlchemy declarative Base and naming conventions.

Classic SQLAlchemy ORM style: :func:`sqlalchemy.orm.declarative_base`.

All ORM models inherit from ``Base``. A consistent naming convention is applied
to automatically generated indexes, unique constraints, check constraints,
foreign keys and primary keys so constraint names are predictable and stable
across environments.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

Base = declarative_base(metadata=metadata)

__all__ = ["Base", "metadata", "NAMING_CONVENTION"]
