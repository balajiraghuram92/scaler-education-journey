from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass


@dataclass(frozen=True)
class CacheStats:
    hits: int
    misses: int
    evictions: int
    size: int
    capacity: int


class LRUCache[K: Hashable, V]:
    """Thread-safe LRU cache with O(1) average get/put.

    - ``capacity < 1`` raises ``ValueError("capacity must be >= 1")``
    - ``get`` / ``put`` / ``get_or_set`` mark the key most recently used
    - when the size exceeds the capacity, the least recently used key is evicted
    - ``key in cache`` and ``len(cache)`` must NOT change recency
    - every operation is protected by a lock
    """

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("Implement LRUCache.__init__")

    def get(self, key: K, default: V | None = None) -> V | None:
        """Return the value (a hit) or ``default`` (a miss)."""
        raise NotImplementedError("Implement get")

    def put(self, key: K, value: V) -> None:
        """Insert or update; evict the LRU key when over capacity (count it in ``evictions``)."""
        raise NotImplementedError("Implement put")

    def get_or_set(self, key: K, factory: Callable[[], V]) -> V:
        """Return the cached value, or call ``factory()`` once, store and return the result.

        The factory runs at most once per missing key, even with concurrent callers.
        A factory that raises must not leave anything cached.
        """
        raise NotImplementedError("Implement get_or_set")

    def __contains__(self, key: object) -> bool:
        raise NotImplementedError("Implement __contains__")

    def __len__(self) -> int:
        raise NotImplementedError("Implement __len__")

    def stats(self) -> CacheStats:
        raise NotImplementedError("Implement stats")
