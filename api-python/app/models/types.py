"""Custom column types for the ported entities."""

from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator


class JsonbText(TypeDecorator[str]):
    """A jsonb column whose Python value is the raw JSON string.

    The C# code stores JSON payloads in jsonb columns as strings
    (e.g. ``MetadataJson``). The impl stays JSONB for DDL/reflection, but both
    processors are bypassed so asyncpg sends/receives the exact string instead
    of double-encoding it or reformatting it on read.
    """

    impl = JSONB
    cache_ok = True

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
