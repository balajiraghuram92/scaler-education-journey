from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import Generic, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class SingleFlightCache(Generic[K, V]):
    """Thread-safe memoizer with single-flight semantics: one computation per key, even under concurrent callers.

    - ``get(key)``: a cached value is returned directly; otherwise exactly ONE caller (the leader) runs
      ``compute(key)`` and every other concurrent caller for that key blocks and receives the same result
    - ``compute`` must run OUTSIDE the internal lock, so a slow key never blocks other keys
    - if ``compute`` raises, every waiter receives the same exception, nothing is cached, and the key leaves the
      in-flight table so a later call retries
    - hand results to waiters with ``concurrent.futures.Future``; never busy-wait
    - ``invalidate(key)`` removes a cached value (no error if absent); ``len(cache)`` is the number of cached values
    """

    def __init__(self, compute: Callable[[K], V]) -> None:
        raise NotImplementedError("Implement SingleFlightCache.__init__")

    def get(self, key: K) -> V:
        raise NotImplementedError("Implement get")

    def invalidate(self, key: K) -> None:
        raise NotImplementedError("Implement invalidate")

    def __len__(self) -> int:
        raise NotImplementedError("Implement __len__")
