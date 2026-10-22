import random

import pytest

from heap_settle import Transfer, apply_transfers, min_transfers_exact, settle_heap


def random_balances(rng: random.Random, n: int) -> dict[str, int]:
    values = [rng.randint(-50, 50) for _ in range(n - 1)]
    values.append(-sum(values))
    return {f"u{i:02d}": v for i, v in enumerate(values)}


def test_largest_matches_largest_and_remainders_are_pushed_back():
    plan = settle_heap({"A": -500, "B": -100, "C": 350, "D": 250})
    assert plan == [Transfer("A", "C", 350), Transfer("A", "D", 150), Transfer("B", "D", 100)]


def test_zero_balances_ignored_and_empty_is_fine():
    assert settle_heap({}) == []
    assert settle_heap({"A": 0, "B": 0}) == []


def test_validation():
    with pytest.raises(ValueError):
        settle_heap({"A": -5, "B": 4})
    with pytest.raises(TypeError):
        settle_heap({"A": -5.0, "B": 5.0})


def test_result_does_not_depend_on_insertion_order():
    rng = random.Random(5)
    balances = random_balances(rng, 9)
    items = list(balances.items())
    reference = settle_heap(balances)
    for _ in range(10):
        rng.shuffle(items)
        assert settle_heap(dict(items)) == reference


def test_plans_clear_everyone_and_are_direct_and_bounded():
    rng = random.Random(1)
    for _ in range(300):
        n = rng.randint(2, 12)
        balances = random_balances(rng, n)
        plan = settle_heap(balances)
        assert apply_transfers(balances, plan) == {}
        non_zero = [u for u, v in balances.items() if v]
        assert len(plan) <= max(len(non_zero) - 1, 0)
        for t in plan:
            assert t.amount > 0
            assert balances[t.payer] < 0 < balances[t.receiver]   # debtor -> creditor only


def test_exact_solver_known_cases():
    assert min_transfers_exact({}) == 0
    assert min_transfers_exact({"A": -5, "B": 5}) == 1
    assert min_transfers_exact({"A": -4, "B": -3, "C": 2, "D": 2, "E": 3}) == 3
    with pytest.raises(ValueError):
        min_transfers_exact({f"u{i}": (1 if i % 2 else -1) for i in range(18)})


def test_greedy_is_never_better_than_exact_and_sometimes_worse():
    rng = random.Random(9)
    worse = 0
    for _ in range(200):
        balances = random_balances(rng, rng.randint(2, 9))
        greedy = len(settle_heap(balances))
        exact = min_transfers_exact(balances)
        assert greedy >= exact
        worse += greedy > exact
    assert worse > 0   # greedy is not optimal


def test_apply_transfers_is_the_oracle():
    plan = [Transfer("A", "C", 300)]
    assert apply_transfers({"A": -300, "B": -200, "C": 500}, plan) == {"B": -200, "C": 200}


def test_tie_breaking_prefers_alphabetically_smallest_user():
    plan = settle_heap({"B": 100, "A": 100, "Y": -100, "X": -100})
    assert plan == [Transfer("X", "A", 100), Transfer("Y", "B", 100)]


def test_exact_solver_ignores_zero_balances_and_finds_groups():
    padded = {f"z{i}": 0 for i in range(30)}
    padded.update({"A": -5, "B": 5, "C": -7, "D": 3, "E": 4})
    assert min_transfers_exact(padded) == 3, "two disjoint zero-sum groups of sizes 2 and 3 -> 5 - 2"
    with pytest.raises(ValueError):
        min_transfers_exact({"A": 1, "B": -2})
