from __future__ import annotations

import contextvars
import json
import logging
import logging.config
from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO, Any

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

_RESERVED = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "request_id"}


@contextmanager
def bind_request_id(value: str) -> Iterator[None]:
    token = request_id.set(value)
    try:
        yield
    finally:
        request_id.reset(token)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        for key, value in vars(record).items():
            if key not in _RESERVED:
                payload[key] = value
        if record.exc_info and record.exc_info[0] is not None:
            payload["exc_type"] = record.exc_info[0].__name__
            payload["exc"] = str(record.exc_info[1])
            cause = record.exc_info[1].__cause__ if record.exc_info[1] else None
            if cause is not None:
                payload["cause"] = f"{type(cause).__name__}: {cause}"
        return json.dumps(payload, sort_keys=True, default=str)


def configure(stream: IO[str], level: str = "INFO") -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"ctx": {"()": ContextFilter}},
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "app": {
                    "class": "logging.StreamHandler",
                    "stream": stream,
                    "formatter": "json",
                    "filters": ["ctx"],
                }
            },
            "loggers": {"gateway": {"level": level, "handlers": ["app"], "propagate": False}},
        }
    )
