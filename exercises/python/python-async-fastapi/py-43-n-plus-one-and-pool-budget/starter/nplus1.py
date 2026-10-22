from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from types import TracebackType

# Schema (created by the tests):
#   conversations(id INTEGER PRIMARY KEY, user_id TEXT)
#   messages(id INTEGER PRIMARY KEY, conversation_id INTEGER, body TEXT)


class QueryCounter:
    """Counts SELECT statements executed on a sqlite3 connection.

    - a context manager that installs ``conn.set_trace_callback`` on entry
    - records only statements whose first keyword is SELECT (case-insensitive) in ``.statements``
    - ``.count`` is the number of recorded statements
    - removes the callback on exit with ``set_trace_callback(None)``, even if the block raised
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self.statements: list[str] = []

    @property
    def count(self) -> int:
        raise NotImplementedError("Implement count")

    def __enter__(self) -> QueryCounter:
        raise NotImplementedError("Implement __enter__")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError("Implement __exit__")


def load_naive(conn: sqlite3.Connection, user_id: str) -> dict[int, list[str]]:
    """Return ``{conversation_id: [message bodies...]}``: one query for the user's conversations
    plus one query per conversation (the N+1 problem). Order by ``id`` everywhere."""
    raise NotImplementedError("Implement load_naive")


def load_batched(conn: sqlite3.Connection, user_id: str, chunk_size: int = 500) -> dict[int, list[str]]:
    """Same result as ``load_naive`` with one query for the conversations plus one
    ``IN (...)`` query per chunk of ``chunk_size`` conversation ids (like ``selectinload``).

    Conversations without messages map to ``[]``. ``chunk_size < 1`` raises ``ValueError``.
    With no conversations, exactly one query is issued.
    """
    raise NotImplementedError("Implement load_batched")


@dataclass(frozen=True)
class Budget:
    worst_case: int
    available: int

    @property
    def fits(self) -> bool:
        """True when the worst case fits within the available connections."""
        raise NotImplementedError("Implement fits")


def connection_budget(
    replicas: int, workers: int, pool_size: int, max_overflow: int, max_connections: int, reserved: int
) -> Budget:
    """``worst_case = replicas * workers * (pool_size + max_overflow)``;
    ``available = max_connections - reserved``."""
    raise NotImplementedError("Implement connection_budget")


def largest_pool_size(
    replicas: int, workers: int, max_connections: int, reserved: int, overflow_ratio: float = 0.5
) -> int:
    """Largest ``pool_size`` such that ``pool_size + int(pool_size * overflow_ratio)`` per worker
    still fits the budget across all replicas and workers, or ``0`` if even a pool of one does not."""
    raise NotImplementedError("Implement largest_pool_size")
