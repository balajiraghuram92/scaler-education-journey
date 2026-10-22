from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

# Table used by import_messages (created by the tests):
#   messages(id INTEGER PRIMARY KEY, conversation_id INT, external_id TEXT, body TEXT,
#            UNIQUE(conversation_id, external_id))


class TransactionAlreadyBegun(RuntimeError):
    pass


class NoActiveTransaction(RuntimeError):
    pass


class UnitOfWork:
    """Explicit transaction boundaries over a sqlite3 connection (like SQLAlchemy's
    ``session.begin()`` and ``session.begin_nested()``)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Keep the connection as the public attribute ``self.conn``.

        The connection must be opened with ``isolation_level=None`` (explicit transaction
        control); otherwise raise ``ValueError``.
        """
        raise NotImplementedError("Implement __init__")

    @property
    def in_transaction(self) -> bool:
        """True while a ``begin()`` block is active."""
        raise NotImplementedError("Implement in_transaction")

    @property
    def depth(self) -> int:
        """Number of currently open savepoints."""
        raise NotImplementedError("Implement depth")

    @contextmanager
    def begin(self) -> Iterator[sqlite3.Connection]:
        """Execute BEGIN, yield the connection, then COMMIT on normal exit or ROLLBACK if any
        exception (including BaseException) escapes, re-raising it.

        Calling it while a transaction is active raises ``TransactionAlreadyBegun`` without
        disturbing the active transaction. After the outermost block exits, no transaction is
        active and ``depth`` is 0.
        """
        raise NotImplementedError("Implement begin")
        yield self.conn  # pragma: no cover  (makes this a generator for @contextmanager)

    @contextmanager
    def begin_nested(self) -> Iterator[sqlite3.Connection]:
        """Execute ``SAVEPOINT <name>`` with a unique name per call. On normal exit issue
        ``RELEASE``; on exception issue ``ROLLBACK TO`` then ``RELEASE`` and re-raise.

        Raises ``NoActiveTransaction`` when no transaction is active.
        """
        raise NotImplementedError("Implement begin_nested")
        yield self.conn  # pragma: no cover


def import_messages(uow: UnitOfWork, conversation_id: int, items: list[tuple[str, str]]) -> tuple[int, int]:
    """Insert ``(external_id, body)`` tuples, each inside its own savepoint, as one transaction.

    ``sqlite3.IntegrityError`` is caught *outside* the savepoint block so a duplicate rolls back
    only its own row. Return ``(saved, skipped)``.
    """
    raise NotImplementedError("Implement import_messages")
