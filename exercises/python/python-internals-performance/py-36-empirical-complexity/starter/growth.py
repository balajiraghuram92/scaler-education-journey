from __future__ import annotations

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
    """For each size, the MINIMUM of ``repeat`` timings divided by ``number`` (seconds per call).

    Build the input with ``make_input(n)`` BEFORE timing, so construction is never timed.
    Use ``timeit.repeat`` and forward ``repeat`` and ``number`` to it.
    """
    raise NotImplementedError("Implement measure")


def growth_exponent(sizes: Sequence[int], times: Sequence[float]) -> float:
    """Least-squares slope of ``log(time)`` against ``log(n)`` (the usual ``cov(x, y) / var(x)``).

    ValueError for fewer than two points, mismatched lengths, non-positive sizes or times,
    or when all sizes are equal.
    """
    raise NotImplementedError("Implement growth_exponent")


def classify(exponent: float) -> str:
    """``"O(1)-ish"`` below 0.4, ``"O(n)-ish"`` below 1.35, ``"O(n^2)-ish"`` below 2.5, else ``"worse than quadratic"``."""
    raise NotImplementedError("Implement classify")


def analyse(
    func: Callable[[T], Any],
    make_input: Callable[[int], T],
    sizes: Sequence[int],
    **kwargs: Any,
) -> tuple[float, str]:
    """Measure, fit the exponent, classify; ``kwargs`` go to ``measure``. Returns ``(exponent, label)``."""
    raise NotImplementedError("Implement analyse")
