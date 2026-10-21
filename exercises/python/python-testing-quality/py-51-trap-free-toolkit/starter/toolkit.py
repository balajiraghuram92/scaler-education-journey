from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Iterator, Sequence


def append_unique[T](item: T, bucket: list[T] | None = None) -> list[T]:
    """Append ``item`` to ``bucket`` if it is not already present and return the list.

    With no bucket, create a FRESH list on every call (no shared mutable default).
    """
    raise NotImplementedError("Implement append_unique")


def make_adders(offsets: Sequence[int]) -> list[Callable[[int], int]]:
    """One adder per offset; each must use its own offset (no late-binding bug)."""
    raise NotImplementedError("Implement make_adders")


def chunked[T](items: Iterable[T], size: int) -> Iterator[list[T]]:
    """Lazily yield lists of at most ``size`` items from ANY iterable (even an infinite one).

    ``size < 1`` raises ``ValueError("size must be >= 1")``.
    """
    raise NotImplementedError("Implement chunked")


def dedupe[H: Hashable](items: Iterable[H]) -> list[H]:
    """Remove duplicates keeping first-seen order, in O(n)."""
    raise NotImplementedError("Implement dedupe")


def top_k_tokens(text: str, k: int) -> list[tuple[str, int]]:
    """Lower-cased tokens matching ``[a-z0-9']+``, most frequent first, ties alphabetical.

    Use a heap-based selection. ``k < 0`` raises ``ValueError``; ``k == 0`` returns ``[]``.
    """
    raise NotImplementedError("Implement top_k_tokens")


def moving_average(values: Iterable[float], window: int) -> list[float]:
    """Trailing averages for FULL windows only, in O(n) using a ``deque``.

    ``window < 1`` raises ``ValueError``.
    """
    raise NotImplementedError("Implement moving_average")


def close_enough(a: float, b: float, *, rel: float = 1e-9, abs_: float = 1e-12) -> bool:
    """Float comparison with ``math.isclose`` and sensible default tolerances."""
    raise NotImplementedError("Implement close_enough")
