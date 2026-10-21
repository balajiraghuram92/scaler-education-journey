from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager


class TransactionAlreadyBegun(RuntimeError):
    pass


class NoActiveTransaction(RuntimeError):
    pass


class UnitOfWork:
    """Explicit transaction boundaries over a sqlite3 connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        if conn.isolation_level is not None:
            raise ValueError("connection must use isolation_level=None (explicit transaction control)")
        self.conn = conn
        self._active = False
        self._savepoints: list[str] = []
        self._counter = 0

    @property
    def in_transaction(self) -> bool:
        return self._active

    @property
    def depth(self) -> int:
        return len(self._savepoints)

    @contextmanager
    def begin(self) -> Iterator[sqlite3.Connection]:
        if self._active:
            raise TransactionAlreadyBegun("a transaction is already begun")
        self.conn.execute("BEGIN")
        self._active = True
        try:
            yield self.conn
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        else:
            self.conn.execute("COMMIT")
        finally:
            self._active = False
            self._savepoints.clear()

    @contextmanager
    def begin_nested(self) -> Iterator[sqlite3.Connection]:
        if not self._active:
            raise NoActiveTransaction("begin_nested() requires an active transaction")
        self._counter += 1
        name = f"sp_{self._counter}"
        self.conn.execute(f"SAVEPOINT {name}")
        self._savepoints.append(name)
        try:
            yield self.conn
        except BaseException:
            self.conn.execute(f"ROLLBACK TO {name}")
            self.conn.execute(f"RELEASE {name}")
            raise
        else:
            self.conn.execute(f"RELEASE {name}")
        finally:
            self._savepoints.pop()


def import_messages(uow: UnitOfWork, conversation_id: int, items: list[tuple[str, str]]) -> tuple[int, int]:
    saved = skipped = 0
    with uow.begin() as conn:
        for external_id, body in items:
            try:
                with uow.begin_nested():
                    conn.execute(
                        "INSERT INTO messages(conversation_id, external_id, body) VALUES (?, ?, ?)",
                        (conversation_id, external_id, body),
                    )
                saved += 1
            except sqlite3.IntegrityError:
                skipped += 1
    return saved, skipped
