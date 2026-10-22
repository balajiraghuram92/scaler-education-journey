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
    def __init__(self, size: int) -> None:
        if size < 1:
            raise ValueError("size must be >= 1")
        self.size = size
        self._idle: queue.Queue[Connection] = queue.Queue(size)
        self._in_use: set[int] = set()
        self._lock = threading.Lock()
        for i in range(size):
            self._idle.put_nowait(Connection(i))

    @property
    def available(self) -> int:
        return self._idle.qsize()

    def acquire(self, timeout: float | None = None) -> Connection:
        try:
            conn = self._idle.get(timeout=timeout)
        except queue.Empty:
            raise PoolTimeout(f"no connection available after {timeout}s") from None
        with self._lock:
            self._in_use.add(conn.id)
        return conn

    def release(self, conn: Connection) -> None:
        with self._lock:
            if conn.id not in self._in_use:
                raise ValueError("connection is not checked out of this pool")
            self._in_use.remove(conn.id)
        self._idle.put_nowait(conn)

    @contextmanager
    def connection(self, timeout: float | None = None) -> Iterator[Connection]:
        conn = self.acquire(timeout)
        try:
            yield conn
        finally:
            self.release(conn)


_pool: ConnectionPool | None = None
_pool_lock = threading.Lock()


def get_pool(size: int | None = None) -> ConnectionPool:
    """Process-wide pool. The first caller decides the size (default 10)."""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ConnectionPool(size if size is not None else 10)
    if size is not None and size != _pool.size:
        raise ValueError(f"pool already created with size {_pool.size}, requested {size}")
    return _pool


def reset_pool() -> None:
    global _pool
    with _pool_lock:
        _pool = None
