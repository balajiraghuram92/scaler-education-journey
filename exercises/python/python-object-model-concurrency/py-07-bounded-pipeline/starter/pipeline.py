from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass


class PipelineClosed(RuntimeError):
    """Raised when submitting to a pipeline that no longer accepts work."""


class Result[R]:
    """Outcome of one item, as a frozen, slotted dataclass.

    Fields: ``seq: int``, ``value: R | None = None``, ``error: Exception | None = None``.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError("Turn Result into a frozen, slotted dataclass")


class Pipeline[T, R]:
    """A fixed pool of worker threads fed by a bounded queue, with graceful shutdown.

    - ``Pipeline(fn, *, workers=4, max_pending=8)``: ``workers < 1`` or ``max_pending < 1``
      raises ``ValueError``; the worker threads start immediately
    - ``submit(item, timeout=None) -> int`` returns the item's sequence number (0, 1, 2, ...);
      it blocks while the queue is full and raises ``queue.Full`` when ``timeout`` expires;
      after ``close()`` it raises ``PipelineClosed``
    - sequence numbers must match queue order even with several producer threads, and no item
      may be lost if ``submit`` races with ``close``
    - workers capture exceptions from ``fn`` into the item's ``Result``; one failure must not
      stop the pipeline; call ``task_done()`` in a ``finally``
    - ``close()`` stops accepting work, lets queued items finish, stops the workers (one sentinel
      per worker, no busy waiting), joins them, and returns the results sorted by ``seq``;
      calling it again returns the same results
    """

    def __init__(self, fn: Callable[[T], R], *, workers: int = 4, max_pending: int = 8) -> None:
        raise NotImplementedError("Implement Pipeline.__init__")

    def submit(self, item: T, timeout: float | None = None) -> int:
        raise NotImplementedError("Implement submit")

    def close(self) -> list[Result[R]]:
        raise NotImplementedError("Implement close")
