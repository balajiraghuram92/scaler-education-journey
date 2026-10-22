from __future__ import annotations

import threading
from collections import OrderedDict
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
    """Thread-safe LRU cache with O(1) get/put, backed by an OrderedDict."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._data: OrderedDict[K, V] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = self._misses = self._evictions = 0

    def get(self, key: K, default: V | None = None) -> V | None:
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)  # most recently used goes last
                self._hits += 1
                return self._data[key]
            self._misses += 1
            return default

    def put(self, key: K, value: V) -> None:
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = value
            if len(self._data) > self._capacity:
                self._data.popitem(last=False)  # evict least recently used
                self._evictions += 1

    def get_or_set(self, key: K, factory: Callable[[], V]) -> V:
        """Return the cached value or compute and store it.

        The lock is held while the factory runs, so it executes at most once per
        missing key, at the cost of blocking other callers meanwhile.
        """
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
                self._hits += 1
                return self._data[key]
            self._misses += 1
            value = factory()
            self.put(key, value)
            return value

    def __contains__(self, key: object) -> bool:
        with self._lock:
            return key in self._data  # does not change recency

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)

    def stats(self) -> CacheStats:
        with self._lock:
            return CacheStats(self._hits, self._misses, self._evictions,
                              len(self._data), self._capacity)
