import sqlite3


def create_tables(conn: sqlite3.Connection) -> None:
    """Create ``expenses`` and ``expense_users`` (idempotent; must not rely on PRAGMA foreign_keys).

    expenses(id INTEGER PRIMARY KEY, description TEXT NOT NULL, amount INTEGER NOT NULL CHECK (amount > 0),
        expense_type TEXT NOT NULL DEFAULT 'NORMAL' CHECK (expense_type IN ('NORMAL','PAYMENT')), group_id INTEGER)
    expense_users(id INTEGER PRIMARY KEY, expense_id INTEGER NOT NULL REFERENCES expenses(id), user TEXT NOT NULL,
        amount INTEGER NOT NULL CHECK (amount > 0), kind TEXT NOT NULL CHECK (kind IN ('PAID','HAD_TO_PAY')))
    """
    raise NotImplementedError("Implement create_tables")


def add_expense(
    conn: sqlite3.Connection,
    description: str,
    rows: list[tuple[str, str, int]],
    expense_type: str = "NORMAL",
    group_id: int | None = None,
) -> int:
    """``rows`` are ``(user, kind, amount)``. ValueError (writing nothing) unless there is at least one PAID and one
    HAD_TO_PAY row and the totals are equal. The expense ``amount`` is the paid total. Insert the expense and all
    rows inside ``with conn:`` so a failure leaves nothing behind. Returns the new expense id."""
    raise NotImplementedError("Implement add_expense")


def record_payment(
    conn: sqlite3.Connection,
    payer: str,
    receiver: str,
    amount: int,
    group_id: int | None = None,
) -> int:
    """Add a PAYMENT expense (payer PAID, receiver HAD_TO_PAY). payer == receiver -> ValueError."""
    raise NotImplementedError("Implement record_payment")


def balances(conn: sqlite3.Connection, group_id: int | None = None) -> dict[str, int]:
    """SUM(PAID) - SUM(HAD_TO_PAY) per user with ONE grouped SELECT ... CASE ... GROUP BY query.
    ``group_id=None`` means all expenses. Zero balances are omitted. No Python loops over rows to compute totals."""
    raise NotImplementedError("Implement balances")


def history(conn: sqlite3.Connection, user: str) -> list[tuple[int, str, str, int]]:
    """``(expense_id, description, kind, amount)`` for every row of ``user``, ordered by expense id then row id."""
    raise NotImplementedError("Implement history")
