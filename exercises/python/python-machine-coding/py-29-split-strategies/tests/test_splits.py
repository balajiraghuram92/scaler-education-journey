import random
from decimal import Decimal
from fractions import Fraction

import pytest

from splits import split_equal, split_exact, split_percentage


def test_equal_split_gives_remainder_to_first_users():
    assert split_equal(1000, ["alice", "bob", "carol"]) == {"alice": 334, "bob": 333, "carol": 333}
    assert list(split_equal(2, ["x", "y", "z"]).items()) == [("x", 1), ("y", 1), ("z", 0)]


@pytest.mark.parametrize(
    "total, users",
    [(0, ["a"]), (-5, ["a"]), (10, []), (10, ["a", "a"]), (1.5, ["a"]), (True, ["a"])],
)
def test_equal_split_validation(total, users):
    with pytest.raises(ValueError):
        split_equal(total, users)


def test_exact_split():
    assert split_exact(1000, {"alice": 700, "bob": 300}) == {"alice": 700, "bob": 300}
    with pytest.raises(ValueError):
        split_exact(1000, {"alice": 700, "bob": 200})
    with pytest.raises(ValueError):
        split_exact(1000, {"alice": 1000, "bob": 0})
    with pytest.raises(ValueError):
        split_exact(1000, {"alice": 500.0, "bob": 500})


def test_percentage_split_largest_remainder():
    shares = split_percentage(100, {"a": "33.333", "b": "33.333", "c": "33.334"})
    assert shares == {"a": 33, "b": 33, "c": 34}
    assert split_percentage(10, {"a": Fraction(100, 3), "b": Fraction(200, 3)}) == {"a": 3, "b": 7}
    assert split_percentage(7, {"a": 50, "b": 50}) == {"a": 4, "b": 3}   # tie -> earlier user
    assert split_percentage(1000, {"a": Decimal("12.5"), "b": Decimal("87.5")}) == {"a": 125, "b": 875}


def test_percentage_validation():
    with pytest.raises(TypeError):
        split_percentage(100, {"a": 50.0, "b": 50})
    with pytest.raises(ValueError):
        split_percentage(100, {"a": 60, "b": 30})
    with pytest.raises(ValueError):
        split_percentage(100, {"a": 110, "b": -10})
    with pytest.raises(ValueError):
        split_percentage(100, {})


def test_shares_always_conserve_the_total_and_stay_within_one_unit():
    rng = random.Random(42)
    for _ in range(300):
        n = rng.randint(1, 7)
        cuts = sorted(rng.sample(range(1, 1000), n - 1)) if n > 1 else []
        parts = [b - a for a, b in zip([0] + cuts, cuts + [1000])]
        percents = {f"u{i}": Fraction(p, 10) for i, p in enumerate(parts)}
        total = rng.randint(1, 10_000)
        shares = split_percentage(total, percents)
        assert sum(shares.values()) == total
        for user, pct in percents.items():
            exact = Fraction(total) * pct / 100
            assert abs(shares[user] - exact) < 1


def test_results_preserve_input_order_and_exact_returns_a_copy():
    users = ["zed", "amy", "bob"]
    assert list(split_equal(10, users)) == users
    source = {"zed": 600, "amy": 400}
    result = split_exact(1000, source)
    assert list(result) == ["zed", "amy"]
    result["zed"] = 0
    assert source["zed"] == 600, "split_exact must not hand back the caller's own dict"


def test_percentage_edge_cases_zero_percent_and_single_user():
    assert split_percentage(99, {"only": 100}) == {"only": 99}
    with pytest.raises(ValueError):
        split_percentage(100, {"a": 100, "b": 0})
    assert split_percentage(1, {"a": "50", "b": "50"}) == {"a": 1, "b": 0}, "one unit goes to the first of a tie"
