from __future__ import annotations

import contextvars
import logging
import logging.config
from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


@contextmanager
def bind_request_id(value: str) -> Iterator[None]:
    """Set ``request_id`` for the duration of the ``with`` block, then RESET it
    using the token returned by ``ContextVar.set``."""
    raise NotImplementedError("Implement bind_request_id")
    yield  # pragma: no cover


class ContextFilter(logging.Filter):
    """Copy the current ``request_id`` value onto every record (``record.request_id``)."""

    def filter(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError("Implement ContextFilter.filter")


class JsonFormatter(logging.Formatter):
    """One JSON object per record, ``sort_keys=True``.

    Fields: ``level``, ``logger``, ``msg`` (the formatted message), ``request_id``,
    every ``extra=`` field, and for exception records ``exc_type``, ``exc`` and (when
    the exception has a ``__cause__``) ``cause`` formatted as ``"<Type>: <message>"``.
    """

    def format(self, record: logging.LogRecord) -> str:
        raise NotImplementedError("Implement JsonFormatter.format")


def configure(stream: IO[str], level: str = "INFO") -> None:
    """Configure the ``gateway`` logger with ``logging.config.dictConfig``:
    a stream handler using ``JsonFormatter`` and ``ContextFilter``,
    ``propagate: False`` and ``disable_existing_loggers: False``."""
    raise NotImplementedError("Implement configure")
