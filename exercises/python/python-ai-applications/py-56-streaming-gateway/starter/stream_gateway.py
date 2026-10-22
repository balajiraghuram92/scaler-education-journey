from __future__ import annotations

import time
from collections import Counter
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field

from fastapi import FastAPI

Upstream = Callable[[str], AsyncIterator[str]]  # prompt -> async iterator of text deltas


@dataclass(slots=True)
class StreamMetrics:
    ttft_ms: list[float] = field(default_factory=list)  # one entry per stream with >= 1 token
    outcomes: Counter[str] = field(default_factory=Counter)  # ok / error / deadline / disconnected


def create_app(upstream: Upstream, *, ping_interval_s: float = 15.0, deadline_s: float = 60.0,
               clock: Callable[[], float] = time.monotonic) -> tuple[FastAPI, StreamMetrics]:
    """Build the app and its metrics. ``POST /chat/stream`` (body ``{"prompt": str}``, min length 1)
    streams Server-Sent Events:

    - headers: ``Content-Type: text/event-stream``, ``Cache-Control: no-cache``, ``X-Accel-Buffering: no``
    - ``event: meta`` + ``data: {"request_id": ...}`` first; then ``data: {"delta": ...}`` per token
      (unnamed events); finally ``event: done`` + ``data: {"tokens": n}``. Every event ends with a blank line.
    - upstream failure mid-stream: ``event: error`` with ``{"code": "upstream_failed", "request_id"}``
      and no exception text; outcome ``error``
    - no token within ``ping_interval_s``: emit ``: ping`` comment lines repeatedly WITHOUT cancelling or
      restarting the pending upstream read (keep one ``anext`` future and ``asyncio.wait`` on it)
    - ``deadline_s`` bounds the whole stream with ``asyncio.timeout``: ``event: error`` with code
      ``deadline_exceeded``; outcome ``deadline``
    - client disconnect: re-raise ``CancelledError`` after recording outcome ``disconnected``; cancel the
      pending read and make sure the upstream generator's cleanup runs (``contextlib.aclosing``)
    - ``ttft_ms`` gets ``(clock() - start) * 1000`` for the first token; record each outcome exactly once
    """
    raise NotImplementedError("Implement create_app")
