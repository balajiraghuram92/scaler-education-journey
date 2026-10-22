from __future__ import annotations

import math
import timeit
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

T = TypeVar("T")


def measure(
    func: Callable[[T], Any],
    make_input: Callable[[int], T],
    sizes: Sequence[int],
    *,
    repeat: int = 3,
    number: int = 1,
) -> list[float]:
    """Best-of-`repeat` seconds per call of func(make_input(n)) for each n in sizes."""
    results: list[float] = []
    for n in sizes:
        data = make_input(n)  # input construction is not timed
        best = min(timeit.repeat(lambda: func(data), repeat=repeat, number=number))
        results.append(best / number)
    return results


def growth_exponent(sizes: Sequence[int], times: Sequence[float]) -> float:
    """Least-squares slope of log(time) against log(n)."""
    if len(sizes) != len(times) or len(sizes) < 2:
        raise ValueError("need at least two (size, time) pairs of equal length")
    if any(n <= 0 for n in sizes) or any(t <= 0 for t in times):
        raise ValueError("sizes and times must be positive")
    xs = [math.log(n) for n in sizes]
    ys = [math.log(t) for t in times]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    var_x = sum((x - mean_x) ** 2 for x in xs)
    if var_x == 0:
        raise ValueError("sizes must not all be equal")
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    return cov / var_x


def classify(exponent: float) -> str:
    if exponent < 0.4:
        return "O(1)-ish"
    if exponent < 1.35:
        return "O(n)-ish"
    if exponent < 2.5:
        return "O(n^2)-ish"
    return "worse than quadratic"


def analyse(
    func: Callable[[T], Any],
    make_input: Callable[[int], T],
    sizes: Sequence[int],
    **kwargs: Any,
) -> tuple[float, str]:
    times = measure(func, make_input, sizes, **kwargs)
    exponent = growth_exponent(sizes, times)
    return exponent, classify(exponent)
