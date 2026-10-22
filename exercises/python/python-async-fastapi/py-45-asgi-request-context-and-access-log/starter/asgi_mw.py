from __future__ import annotations

import contextvars
import json
import re
import time
import uuid
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class RequestContextMiddleware:
    """Pure ASGI middleware: accept or generate a request ID and echo it in the response.

    - for any ``scope["type"]`` other than ``"http"``, pass straight to the inner app
    - ASGI header names are lowercase bytes; read the inbound ``header`` (default ``b"x-request-id"``)
    - accept an inbound value only if it matches ``_SAFE_ID`` (protects against log injection),
      otherwise generate ``uuid.uuid4().hex``
    - set ``request_id_var`` before calling the inner app, and always reset it with the token
      afterwards (also when the inner app raises)
    - append ``(header, id)`` to the headers of the ``http.response.start`` message
    """

    def __init__(self, app: ASGIApp, header: bytes = b"x-request-id") -> None:
        raise NotImplementedError("Implement RequestContextMiddleware.__init__")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotImplementedError("Implement RequestContextMiddleware.__call__")


class AccessLogMiddleware:
    """Pure ASGI middleware: emit exactly one JSON log line per HTTP request.

    - for any ``scope["type"]`` other than ``"http"``, pass straight to the inner app
    - call ``emit(line)`` once per request from a ``finally`` block, with
      ``json.dumps({...}, separators=(",", ":"))`` of
      ``{"request_id", "method", "path", "status", "duration_ms"}``
    - ``status`` comes from the ``http.response.start`` message and defaults to 500 if the inner
      app raised before responding
    - ``duration_ms`` is measured with ``clock`` and rounded to one decimal
    - exceptions from the inner app propagate unchanged
    - it must be nested *inside* RequestContextMiddleware so the log shows the request ID
    """

    def __init__(
        self, app: ASGIApp, emit: Callable[[str], None], clock: Callable[[], float] = time.perf_counter
    ) -> None:
        raise NotImplementedError("Implement AccessLogMiddleware.__init__")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotImplementedError("Implement AccessLogMiddleware.__call__")
