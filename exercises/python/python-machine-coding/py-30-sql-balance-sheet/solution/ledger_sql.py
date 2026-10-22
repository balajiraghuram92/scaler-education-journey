import sqlite3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),
    expense_type TEXT NOT NULL DEFAULT 'NORMAL'
        CHECK (expense_type IN ('NORMAL', 'PAYMENT')),
    group_id INTEGER
);
CREATE TABLE IF NOT EXISTS expense_users (
    id INTEGER PRIMARY KEY,
    expense_id INTEGER NOT NULL REFERENCES expenses(id),
    user TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),
    kind TEXT NOT NULL CHECK (kind IN ('PAID', 'HAD_TO_PAY'))
);
"""


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)


def add_expense(
    conn: sqlite3.Connection,
    description: str,
    rows: list[tuple[str, str, int]],
    expense_type: str = "NORMAL",
    group_id: int | None = None,
) -> int:
    paid = sum(amount for _, kind, amount in rows if kind == "PAID")
    owed = sum(amount for _, kind, amount in rows if kind == "HAD_TO_PAY")
    has_paid = any(kind == "PAID" for _, kind, _ in rows)
    has_owed = any(kind == "HAD_TO_PAY" for _, kind, _ in rows)
    if not (has_paid and has_owed):
        raise ValueError("an expense needs PAID and HAD_TO_PAY rows")
    if paid != owed:
        raise ValueError(f"paid {paid} != owed {owed}")
    with conn:
        cur = conn.execute(
            "INSERT INTO expenses (description, amount, expense_type, group_id) VALUES (?, ?, ?, ?)",
            (description, paid, expense_type, group_id),
        )
        expense_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO expense_users (expense_id, user, amount, kind) VALUES (?, ?, ?, ?)",
            [(expense_id, user, amount, kind) for user, kind, amount in rows],
        )
    return expense_id


def record_payment(
    conn: sqlite3.Connection,
    payer: str,
    receiver: str,
    amount: int,
    group_id: int | None = None,
) -> int:
    if payer == receiver:
        raise ValueError("payer and receiver must differ")
    return add_expense(
        conn,
        "Payment",
        [(payer, "PAID", amount), (receiver, "HAD_TO_PAY", amount)],
        expense_type="PAYMENT",
        group_id=group_id,
    )


def balances(conn: sqlite3.Connection, group_id: int | None = None) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT eu.user,
               SUM(CASE WHEN eu.kind = 'PAID' THEN eu.amount ELSE -eu.amount END) AS total
        FROM expense_users eu
        JOIN expenses e ON e.id = eu.expense_id
        WHERE (? IS NULL OR e.group_id = ?)
        GROUP BY eu.user
        HAVING total != 0
        """,
        (group_id, group_id),
    )
    return {user: total for user, total in rows}


def history(conn: sqlite3.Connection, user: str) -> list[tuple[int, str, str, int]]:
    rows = conn.execute(
        """
        SELECT e.id, e.description, eu.kind, eu.amount
        FROM expense_users eu
        JOIN expenses e ON e.id = eu.expense_id
        WHERE eu.user = ?
        ORDER BY e.id, eu.id
        """,
        (user,),
    )
    return [tuple(row) for row in rows]
