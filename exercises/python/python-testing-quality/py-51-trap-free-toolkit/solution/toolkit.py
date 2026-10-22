from __future__ import annotations

import heapq
import math
import re
from collections import Counter, deque
from collections.abc import Callable, Hashable, Iterable, Iterator, Sequence
from itertools import islice


def append_unique[T](item: T, bucket: list[T] | None = None) -> list[T]:
    """Append item to bucket if absent. A fresh list is created per call by default."""
    target: list[T] = [] if bucket is None else bucket
    if item not in target:
        target.append(item)
    return target


def make_adders(offsets: Sequence[int]) -> list[Callable[[int], int]]:
    """One adder per offset; each remembers its own offset (no late binding)."""
    return [lambda x, offset=offset: x + offset for offset in offsets]


def chunked[T](items: Iterable[T], size: int) -> Iterator[list[T]]:
    """Yield lists of at most `size` items from any iterable, lazily."""
    if size < 1:
        raise ValueError("size must be >= 1")
    iterator = iter(items)
    while chunk := list(islice(iterator, size)):
        yield chunk


def dedupe[H: Hashable](items: Iterable[H]) -> list[H]:
    """Remove duplicates, keeping first-seen order, in O(n)."""
    return list(dict.fromkeys(items))


def top_k_tokens(text: str, k: int) -> list[tuple[str, int]]:
    """Most frequent tokens; ties broken alphabetically for determinism."""
    if k < 0:
        raise ValueError("k must be >= 0")
    counts = Counter(re.findall(r"[a-z0-9']+", text.lower()))
    return heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))


def moving_average(values: Iterable[float], window: int) -> list[float]:
    """Trailing moving average in O(n) using a deque and a running sum."""
    if window < 1:
        raise ValueError("window must be >= 1")
    buf: deque[float] = deque()
    out: list[float] = []
    for v in values:
        buf.append(v)
        if len(buf) > window:
            buf.popleft()
        if len(buf) == window:
            out.append(math.fsum(buf) / window)
    return out


def close_enough(a: float, b: float, *, rel: float = 1e-9, abs_: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)
