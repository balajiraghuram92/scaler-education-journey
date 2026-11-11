"""SQLAlchemy base for all ported entities.

Conventions mirror EF Core Npgsql defaults so reflected metadata matches:
primary keys, timestamptz datetimes, and explicit constraint/index names taken
from api/Data/StudyTrackerContext.cs and the EF model snapshot.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# EF Core default constraint names: PK_<table>, FK_<dependent>_<principal>_<column>.
CONVENTION = {
    "pk": "PK_%(table_name)s",
    "fk": "FK_%(table_name)s_%(referred_table_name)s_%(first_column_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENTION)
