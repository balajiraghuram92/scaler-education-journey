"""Custom column types for the ported entities."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy import Text, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.types import TypeDecorator


class JsonbText(TypeDecorator[str]):
    """A jsonb column whose Python value is PostgreSQL's text rendering.

    The C# code maps these as ``string`` properties, so Npgsql returns
    PostgreSQL's own text form (a space after each ``:`` and ``,``) and
    the port must serve the same text. The asyncpg driver hands
    SQLAlchemy a decoded ``dict``, so the column is selected through
    ``CAST(col AS TEXT)`` and the result passes through as ``str``. A
    ``dict``/``list`` that still arrives falls back to
    ``stjson.dumps``. Writes send the string as is, exactly as before.
    """

    impl = JSONB
    cache_ok = True

    def column_expression(self, colexpr: ColumnElement[Any]) -> ColumnElement[Any]:
        return cast(colexpr, Text)

    def bind_processor(self, dialect: Dialect) -> Callable[[Any], Any] | None:
        return None

    def result_processor(
        self, dialect: Dialect, coltype: object
    ) -> Callable[[Any], Any] | None:
        def process(value: Any) -> Any:
            if value is None or isinstance(value, str):
                return value
            from ..stjson import dumps

            return dumps(value)

        return process
