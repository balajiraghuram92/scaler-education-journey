from __future__ import annotations

import sqlite3
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from types import TracebackType


class QueryCounter:
    """Counts SELECT statements executed on a sqlite3 connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self.statements: list[str] = []

    @property
    def count(self) -> int:
        return len(self.statements)

    def __enter__(self) -> QueryCounter:
        self._conn.set_trace_callback(self._record)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._conn.set_trace_callback(None)

    def _record(self, statement: str) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            self.statements.append(statement)


def load_naive(conn: sqlite3.Connection, user_id: str) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    parents = conn.execute("SELECT id FROM conversations WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
    for (cid,) in parents:
        rows = conn.execute("SELECT body FROM messages WHERE conversation_id = ? ORDER BY id", (cid,)).fetchall()
        result[cid] = [body for (body,) in rows]
    return result


def _chunks(items: list[int], size: int) -> Iterator[list[int]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]


def load_batched(conn: sqlite3.Connection, user_id: str, chunk_size: int = 500) -> dict[int, list[str]]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    ids = [cid for (cid,) in conn.execute("SELECT id FROM conversations WHERE user_id = ? ORDER BY id", (user_id,))]
    grouped: dict[int, list[str]] = defaultdict(list)
    for chunk in _chunks(ids, chunk_size):
        marks = ",".join("?" * len(chunk))
        sql = f"SELECT conversation_id, body FROM messages WHERE conversation_id IN ({marks}) ORDER BY id"
        for cid, body in conn.execute(sql, chunk):
            grouped[cid].append(body)
    return {cid: grouped.get(cid, []) for cid in ids}


@dataclass(frozen=True)
class Budget:
    worst_case: int
    available: int

    @property
    def fits(self) -> bool:
        return self.worst_case <= self.available


def connection_budget(
    replicas: int, workers: int, pool_size: int, max_overflow: int, max_connections: int, reserved: int
) -> Budget:
    return Budget(replicas * workers * (pool_size + max_overflow), max_connections - reserved)


def largest_pool_size(
    replicas: int, workers: int, max_connections: int, reserved: int, overflow_ratio: float = 0.5
) -> int:
    available = max_connections - reserved
    best = 0
    size = 1
    while replicas * workers * (size + int(size * overflow_ratio)) <= available:
        best = size
        size += 1
    return best
