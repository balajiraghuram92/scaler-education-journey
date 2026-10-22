import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass


class PoolTimeout(Exception):
    """No connection became available within the timeout."""


@dataclass(eq=False)
class Connection:
    id: int


class ConnectionPool:
    """Fixed-size pool with timeouts, a context manager and double-release detection.

    - ``size < 1`` raises ValueError; ``size`` is a public attribute.
    - ``acquire(timeout=None)`` blocks up to ``timeout`` seconds, then raises PoolTimeout.
    - ``release(conn)`` raises ValueError if ``conn`` is not currently checked out.
    - ``connection(timeout=None)`` is a context manager that always releases.
    - ``available`` is the number of idle connections.
    """

    def __init__(self, size: int) -> None:
        raise NotImplementedError("Implement the constructor")

    @property
    def available(self) -> int:
        raise NotImplementedError("Implement available")

    def acquire(self, timeout: float | None = None) -> Connection:
        raise NotImplementedError("Implement acquire")

    def release(self, conn: Connection) -> None:
        raise NotImplementedError("Implement release")

    @contextmanager
    def connection(self, timeout: float | None = None) -> Iterator[Connection]:
        raise NotImplementedError("Implement connection")
        yield  # pragma: no cover


def get_pool(size: int | None = None) -> ConnectionPool:
    """Process-wide pool, created lazily and thread-safely (default size 10).

    A later call with an explicit size that differs from the existing pool's
    size raises ValueError instead of silently ignoring it.
    """
    raise NotImplementedError("Implement get_pool")


def reset_pool() -> None:
    """Forget the process-wide pool (test hook)."""
    raise NotImplementedError("Implement reset_pool")
