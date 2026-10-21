import timeit

import pytest

import growth
from growth import analyse, classify, growth_exponent, measure

# NOTE: nothing in this suite depends on real wall-clock time. Tests that go through `measure` / `analyse`
# replace `timeit.repeat` with a fake that reports a synthetic duration derived from the input size.


def test_exponent_of_exact_power_laws() -> None:
    sizes = [1000, 2000, 4000, 8000]
    assert growth_exponent(sizes, [n * 1e-6 for n in sizes]) == pytest.approx(1.0), "time ~ n has exponent 1"
    assert growth_exponent(sizes, [n * n * 1e-9 for n in sizes]) == pytest.approx(2.0), "time ~ n^2 has exponent 2"
    assert growth_exponent(sizes, [5e-6 for _ in sizes]) == pytest.approx(0.0, abs=1e-9), "constant time has exponent 0"


def test_exponent_is_a_least_squares_fit_over_all_points() -> None:
    # sizes 1, 2, 4 are evenly spaced in log space, so the fitted slope depends only on the end points.
    # A first-two-points shortcut would give log(3)/log(2) = 1.58 instead.
    assert growth_exponent([1, 2, 4], [1.0, 3.0, 4.0]) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "exponent, label",
    [
        (-1.0, "O(1)-ish"),
        (0.0, "O(1)-ish"),
        (0.39, "O(1)-ish"),
        (0.4, "O(n)-ish"),
        (1.0, "O(n)-ish"),
        (1.34, "O(n)-ish"),
        (1.35, "O(n^2)-ish"),
        (2.0, "O(n^2)-ish"),
        (2.49, "O(n^2)-ish"),
        (2.5, "worse than quadratic"),
        (3.0, "worse than quadratic"),
    ],
)
def test_classify(exponent: float, label: str) -> None:
    assert classify(exponent) == label, f"classify({exponent}) should be {label!r}"


@pytest.mark.parametrize(
    "sizes, times",
    [([1], [1.0]), ([1, 2], [1.0]), ([1, 1], [1.0, 2.0]), ([0, 2], [1.0, 2.0]), ([1, 2], [0.0, 1.0])],
)
def test_invalid_measurements_raise(sizes, times) -> None:
    with pytest.raises(ValueError):
        growth_exponent(sizes, times)


def test_measure_returns_one_non_negative_time_per_size() -> None:
    times = measure(lambda xs: sum(xs), lambda n: list(range(n)), [100, 200, 400], repeat=2)
    assert len(times) == 3, "one timing per size"
    assert all(isinstance(t, float) and t >= 0 for t in times)


def _patch_timeit(monkeypatch: pytest.MonkeyPatch, sizes_seen: list[int], cost) -> None:
    """Fake timeit.repeat: run the statement once, report cost(last_seen_size) for each repeat."""

    def fake_repeat(stmt, setup="pass", timer=None, repeat=5, number=1, globals=None):
        stmt()
        return [cost(sizes_seen[-1])] * repeat

    monkeypatch.setattr(timeit, "repeat", fake_repeat)
    if hasattr(growth, "repeat"):  # `from timeit import repeat` style
        monkeypatch.setattr(growth, "repeat", fake_repeat)


def test_measure_takes_the_minimum_divides_by_number_and_does_not_time_input_construction(monkeypatch) -> None:
    built: list[int] = []
    sizes_seen: list[int] = []

    def fake_repeat(stmt, setup="pass", timer=None, repeat=5, number=1, globals=None):
        stmt()
        assert repeat == 4 and number == 5, "repeat and number must be forwarded to timeit.repeat"
        return [0.9, 0.5, 0.7, 0.6]

    monkeypatch.setattr(timeit, "repeat", fake_repeat)
    if hasattr(growth, "repeat"):
        monkeypatch.setattr(growth, "repeat", fake_repeat)

    def make_input(n: int) -> list[int]:
        built.append(n)
        return [0] * n

    times = measure(lambda xs: sizes_seen.append(len(xs)), make_input, [10, 20, 30], repeat=4, number=5)
    assert times == pytest.approx([0.1, 0.1, 0.1]), "minimum of the repeats (0.5) divided by number (5)"
    assert built == [10, 20, 30], "make_input must be called once per size, outside the timed statement"
    assert sizes_seen == [10, 20, 30], "the function under test must receive the built input"


@pytest.mark.parametrize(
    "cost, expected_exponent, expected_label",
    [
        (lambda n: 1e-6, 0.0, "O(1)-ish"),
        (lambda n: n * 1e-9, 1.0, "O(n)-ish"),
        (lambda n: n * n * 1e-12, 2.0, "O(n^2)-ish"),
        (lambda n: n**3 * 1e-15, 3.0, "worse than quadratic"),
    ],
)
def test_analyse_ties_measurement_fit_and_classification_together(
    monkeypatch, cost, expected_exponent, expected_label
) -> None:
    sizes_seen: list[int] = []
    _patch_timeit(monkeypatch, sizes_seen, cost)
    exponent, label = analyse(lambda xs: sizes_seen.append(len(xs)), lambda n: [0] * n, [1000, 2000, 4000])
    assert exponent == pytest.approx(expected_exponent, abs=1e-6)
    assert label == expected_label
