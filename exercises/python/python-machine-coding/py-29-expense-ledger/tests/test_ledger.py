import pytest

from ledger import (
    Expense,
    ExpenseKind,
    ExpenseUser,
    LedgerError,
    RowType,
    expenses_for_user,
    net_balances,
    record_settlement,
)

PAID, OWED = RowType.PAID, RowType.HAD_TO_PAY


def dinner() -> Expense:
    return Expense(
        1,
        (
            ExpenseUser("A", PAID, 900),
            ExpenseUser("A", OWED, 300),
            ExpenseUser("B", OWED, 300),
            ExpenseUser("C", OWED, 300),
        ),
    )


def test_net_balances_of_one_expense():
    assert net_balances([dinner()]) == {"A": 600, "B": -300, "C": -300}


def test_user_who_paid_exactly_their_share_is_omitted():
    e = Expense(1, (ExpenseUser("A", PAID, 100), ExpenseUser("A", OWED, 100), ExpenseUser("B", PAID, 50), ExpenseUser("C", OWED, 50)))
    assert net_balances([e]) == {"B": 50, "C": -50}


def test_balances_sum_to_zero_across_many_expenses():
    cab = Expense(2, (ExpenseUser("B", PAID, 200), ExpenseUser("A", OWED, 100), ExpenseUser("B", OWED, 100)))
    balances = net_balances([dinner(), cab])
    assert balances == {"A": 500, "B": -200, "C": -300}
    assert sum(balances.values()) == 0


def test_unbalanced_expense_is_rejected():
    with pytest.raises(LedgerError):
        Expense(1, (ExpenseUser("A", PAID, 600), ExpenseUser("B", OWED, 250), ExpenseUser("C", OWED, 250)))


def test_expense_needs_both_row_types():
    with pytest.raises(LedgerError):
        Expense(1, (ExpenseUser("A", PAID, 10),))
    with pytest.raises(LedgerError):
        Expense(1, (ExpenseUser("A", OWED, 10),))
    with pytest.raises(LedgerError):
        Expense(1, ())


@pytest.mark.parametrize("bad", [0, -5, 1.5, True])
def test_amounts_must_be_positive_integers(bad):
    with pytest.raises(LedgerError):
        ExpenseUser("A", PAID, bad)


def test_settlement_is_a_payment_expense_that_moves_balances():
    pay = record_settlement(2, "B", "A", 300)
    assert pay.kind is ExpenseKind.PAYMENT
    assert net_balances([dinner(), pay]) == {"A": 300, "C": -300}


def test_payment_rules():
    with pytest.raises(LedgerError):
        record_settlement(3, "A", "A", 10)
    with pytest.raises(LedgerError):
        Expense(
            3,
            (ExpenseUser("A", PAID, 10), ExpenseUser("B", OWED, 5), ExpenseUser("C", OWED, 5)),
            ExpenseKind.PAYMENT,
        )


def test_expenses_for_user_sorted_and_filtered():
    pay = record_settlement(0, "B", "A", 300)
    other = Expense(5, (ExpenseUser("X", PAID, 10), ExpenseUser("Y", OWED, 10)))
    result = expenses_for_user([other, dinner(), pay], "A")
    assert [e.expense_id for e in result] == [0, 1]
    assert expenses_for_user([other], "A") == []


def test_expense_is_immutable():
    e = dinner()
    with pytest.raises(Exception):
        e.expense_id = 99
