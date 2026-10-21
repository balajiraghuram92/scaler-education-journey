import random

import pytest

from settle_up import (
    Expense,
    ExpenseUser,
    NaiveSettleUpStrategy,
    RowType,
    SettleUpService,
    SettleUpStrategy,
    Transaction,
    build_dummy_expense,
    net_balances,
)

P, O = RowType.PAID, RowType.HAD_TO_PAY


def expense(i, paid, owed, group_id=None):
    rows = tuple(ExpenseUser(u, P, a) for u, a in paid.items()) + tuple(
        ExpenseUser(u, O, a) for u, a in owed.items()
    )
    return Expense(i, rows, group_id)


def apply(balances, transactions):
    result = dict(balances)
    for t in transactions:
        result[t.payer] = result.get(t.payer, 0) + t.amount
        result[t.receiver] = result.get(t.receiver, 0) - t.amount
    return {u: v for u, v in result.items() if v}


def test_net_balances():
    e = expense(1, {"A": 900}, {"A": 300, "B": 300, "C": 300})
    assert net_balances([e]) == {"A": 600, "B": -300, "C": -300}


def test_naive_strategy_chains_through_the_next_person():
    e = expense(1, {"C": 500}, {"A": 300, "B": 200})
    txns = NaiveSettleUpStrategy().settle([e])
    assert [str(t) for t in txns] == ["A pays B 300", "B pays C 500"]


def test_naive_strategy_clears_all_balances_and_stays_within_n_minus_1():
    rng = random.Random(3)
    users = "ABCDEFG"
    for i in range(200):
        expenses = []
        for j in range(rng.randint(1, 6)):
            payer = rng.choice(users)
            sharers = rng.sample(users, rng.randint(1, 5))
            total = rng.randint(1, 900)
            base, extra = divmod(total, len(sharers))
            owed = {u: base + (1 if k < extra else 0) for k, u in enumerate(sharers)}
            owed = {u: a for u, a in owed.items() if a > 0}
            expenses.append(expense(j, {payer: total}, owed))
        balances = net_balances(expenses)
        txns = NaiveSettleUpStrategy().settle(expenses)
        assert apply(balances, txns) == {}
        assert len(txns) <= max(len(balances) - 1, 0)
        assert all(t.amount > 0 and t.payer != t.receiver for t in txns)


def test_settle_up_user_filters_to_transactions_involving_the_user():
    e = expense(1, {"C": 500}, {"A": 300, "B": 200})
    service = SettleUpService([e], NaiveSettleUpStrategy())
    assert [str(t) for t in service.settle_up_user("A")] == ["A pays B 300"]
    assert [str(t) for t in service.settle_up_user("B")] == ["A pays B 300", "B pays C 500"]
    assert service.settle_up_user("Z") == []


def test_settle_up_user_includes_ungrouped_and_all_group_expenses():
    in_group_1 = expense(1, {"A": 100}, {"A": 50, "B": 50}, group_id=1)
    in_group_2 = expense(2, {"C": 100}, {"A": 50, "C": 50}, group_id=2)
    one_to_one = expense(3, {"B": 40}, {"A": 40})
    unrelated = expense(4, {"X": 10}, {"Y": 10}, group_id=1)
    seen: list[list[int]] = []

    class Spy(SettleUpStrategy):
        def settle(self, expenses):
            seen.append(sorted(e.expense_id for e in expenses))
            return []

    SettleUpService([in_group_1, in_group_2, one_to_one, unrelated], Spy()).settle_up_user("A")
    assert seen == [[1, 2, 3]]


def test_settle_up_group_only_uses_that_group():
    g1 = expense(1, {"A": 100}, {"B": 100}, group_id=1)
    g2 = expense(2, {"C": 100}, {"D": 100}, group_id=2)
    service = SettleUpService([g1, g2], NaiveSettleUpStrategy())
    assert [str(t) for t in service.settle_up_group(1)] == ["B pays A 100"]


def test_dummy_expense_moves_balances_and_validates():
    dinner = expense(1, {"A": 900}, {"A": 300, "B": 300, "C": 300})
    pay = build_dummy_expense(2, "B", "A", 300)
    assert net_balances([dinner, pay]) == {"A": 300, "C": -300}
    with pytest.raises(ValueError):
        build_dummy_expense(3, "A", "A", 5)
    with pytest.raises(ValueError):
        build_dummy_expense(3, "A", "B", 0)


def test_strategy_is_abstract_and_swappable():
    with pytest.raises(TypeError):
        SettleUpStrategy()

    class Fixed(SettleUpStrategy):
        def settle(self, expenses):
            return [Transaction("A", "B", 1)]

    e = expense(1, {"B": 5}, {"A": 5})
    assert SettleUpService([e], Fixed()).settle_up_group is not None
    assert SettleUpService([e], Fixed()).settle_up_user("A") == [Transaction("A", "B", 1)]


def test_transaction_string_and_empty_input():
    assert str(Transaction("A", "B", 70)) == "A pays B 70"
    assert NaiveSettleUpStrategy().settle([]) == []
    balanced = expense(1, {"A": 10}, {"A": 10})
    assert NaiveSettleUpStrategy().settle([balanced]) == [], "nothing to settle when everyone is even"
    service = SettleUpService([], NaiveSettleUpStrategy())
    assert service.settle_up_group(99) == []
