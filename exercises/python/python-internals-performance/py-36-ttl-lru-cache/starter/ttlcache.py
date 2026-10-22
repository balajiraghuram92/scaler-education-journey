from __future__ import annotations

import time
from collections.abc import Callable
from typing import NamedTuple, ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class CacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: int
    currsize: int


class Cached(Protocol[P, R]):
    """What the decorator returns: the wrapped callable plus ``cache_info`` and ``cache_clear``."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def cache_info(self) -> CacheInfo: ...
    def cache_clear(self) -> None: ...


def ttl_cache(
    maxsize: int = 128,
    ttl: float = 60.0,
    clock: Callable[[], float] = time.monotonic,
) -> Callable[[Callable[P, R]], Cached[P, R]]:
    """LRU cache whose entries also expire ``ttl`` seconds after being stored.

    - ValueError if ``maxsize < 1`` or ``ttl <= 0`` (raised when ``ttl_cache(...)`` is called)
    - hit: an entry for the same positional + keyword arguments exists and ``clock() - stored_at < ttl``
      (at exactly ``ttl`` seconds it is expired); a hit counts as a use for LRU and does not extend the ttl
    - miss: call the function (OUTSIDE the lock), store the result, evict the least recently used entry beyond ``maxsize``
    - unhashable arguments raise TypeError; exceptions propagate and nothing is cached
    - delete an expired entry on lookup so ``currsize`` does not count stale items
    - ``functools.wraps`` metadata preserved; ``cache_info()`` -> ``CacheInfo``; ``cache_clear()`` empties the cache
      and resets the counters; protect shared state with a ``threading.Lock``
    """
    raise NotImplementedError("Implement ttl_cache")
