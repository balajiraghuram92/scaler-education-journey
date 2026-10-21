import random
import sqlite3
from collections import defaultdict

import pytest

from ledger_sql import add_expense, balances, create_tables, history, record_payment


def make() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)
    return conn


DINNER = [("A", "PAID", 900), ("A", "HAD_TO_PAY", 300), ("B", "HAD_TO_PAY", 300), ("C", "HAD_TO_PAY", 300)]


def test_balances_and_settlement_without_special_case():
    conn = make()
    add_expense(conn, "Dinner", DINNER)
    assert balances(conn) == {"A": 600, "B": -300, "C": -300}
    record_payment(conn, "B", "A", 300)
    assert balances(conn) == {"A": 300, "C": -300}
    record_payment(conn, "C", "A", 300)
    assert balances(conn) == {}


def test_unbalanced_or_one_sided_expense_writes_nothing():
    conn = make()
    with pytest.raises(ValueError):
        add_expense(conn, "Bad", [("A", "PAID", 600), ("B", "HAD_TO_PAY", 500)])
    with pytest.raises(ValueError):
        add_expense(conn, "Bad2", [("A", "PAID", 600)])
    assert conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM expense_users").fetchone()[0] == 0


def test_a_failure_midway_rolls_back_the_expense_row():
    conn = make()
    with pytest.raises(sqlite3.IntegrityError):
        # second row violates CHECK (amount > 0); the expense row must not survive
        add_expense(conn, "Odd", [("A", "PAID", 0), ("B", "HAD_TO_PAY", 0)])
    assert conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 0


def test_group_filter():
    conn = make()
    add_expense(conn, "Trip", DINNER, group_id=1)
    add_expense(conn, "Cab", [("B", "PAID", 200), ("A", "HAD_TO_PAY", 200)], group_id=2)
    assert balances(conn, group_id=1) == {"A": 600, "B": -300, "C": -300}
    assert balances(conn, group_id=2) == {"B": 200, "A": -200}
    assert balances(conn) == {"A": 400, "B": -100, "C": -300}


def test_history_for_user():
    conn = make()
    add_expense(conn, "Dinner", DINNER)
    record_payment(conn, "B", "A", 300)
    assert history(conn, "B") == [(1, "Dinner", "HAD_TO_PAY", 300), (2, "Payment", "PAID", 300)]
    assert history(conn, "Z") == []


def test_payer_must_differ_from_receiver():
    with pytest.raises(ValueError):
        record_payment(make(), "A", "A", 10)


def test_sql_balances_match_python_on_random_data():
    rng = random.Random(11)
    conn = make()
    users = ["A", "B", "C", "D", "E"]
    for i in range(60):
        payer = rng.choice(users)
        total = rng.randint(1, 5000)
        sharers = rng.sample(users, rng.randint(1, len(users)))
        base, extra = divmod(total, len(sharers))
        rows = [(payer, "PAID", total)] + [
            (u, "HAD_TO_PAY", base + (1 if j < extra else 0))
            for j, u in enumerate(sharers)
            if base + (1 if j < extra else 0) > 0
        ]
        add_expense(conn, f"e{i}", rows, group_id=rng.choice([None, 1, 2]))
    expected: dict[str, int] = defaultdict(int)
    for user, kind, amount in conn.execute("SELECT user, kind, amount FROM expense_users"):
        expected[user] += amount if kind == "PAID" else -amount
    expected = {u: v for u, v in expected.items() if v != 0}
    got = balances(conn)
    assert got == expected
    assert sum(got.values()) == 0


def test_create_tables_is_idempotent_and_keeps_data():
    conn = make()
    add_expense(conn, "Dinner", DINNER)
    create_tables(conn)
    assert balances(conn) == {"A": 600, "B": -300, "C": -300}


def test_expense_amount_is_paid_total_and_payment_is_typed():
    conn = make()
    eid = add_expense(conn, "Dinner", DINNER, group_id=3)
    pid = record_payment(conn, "B", "A", 300, group_id=3)
    rows = {r[0]: r for r in conn.execute("SELECT id, amount, expense_type, group_id FROM expenses")}
    assert rows[eid][1:] == (900, "NORMAL", 3)
    assert rows[pid][1:] == (300, "PAYMENT", 3)
    assert balances(make()) == {}, "an empty ledger has no balances"
