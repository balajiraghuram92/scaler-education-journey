from __future__ import annotations

import threading
from collections.abc import Callable, Hashable
from concurrent.futures import Future
from typing import Generic, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class SingleFlightCache(Generic[K, V]):
    """Thread-safe memoizer: one computation per key, even under concurrent callers."""

    def __init__(self, compute: Callable[[K], V]) -> None:
        self._compute = compute
        self._lock = threading.Lock()
        self._values: dict[K, V] = {}
        self._inflight: dict[K, Future[V]] = {}

    def get(self, key: K) -> V:
        with self._lock:
            if key in self._values:
                return self._values[key]
            future = self._inflight.get(key)
            leader = future is None
            if future is None:
                future = self._inflight[key] = Future()
        if leader:
            self._run_leader(key, future)
        return future.result()  # waiters block here; exceptions propagate

    def _run_leader(self, key: K, future: Future[V]) -> None:
        try:
            value = self._compute(key)  # runs outside the lock: other keys proceed
        except BaseException as exc:
            with self._lock:
                del self._inflight[key]  # failures are not cached
            future.set_exception(exc)
        else:
            with self._lock:
                self._values[key] = value
                del self._inflight[key]
            future.set_result(value)

    def invalidate(self, key: K) -> None:
        with self._lock:
            self._values.pop(key, None)

    def __len__(self) -> int:
        with self._lock:
            return len(self._values)
