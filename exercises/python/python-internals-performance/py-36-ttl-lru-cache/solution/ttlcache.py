from __future__ import annotations

import functools
import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Hashable
from typing import Any, NamedTuple, ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class CacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: int
    currsize: int


class Cached(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def cache_info(self) -> CacheInfo: ...
    def cache_clear(self) -> None: ...


def ttl_cache(
    maxsize: int = 128,
    ttl: float = 60.0,
    clock: Callable[[], float] = time.monotonic,
) -> Callable[[Callable[P, R]], Cached[P, R]]:
    """LRU cache whose entries also expire `ttl` seconds after being stored."""
    if maxsize < 1 or ttl <= 0:
        raise ValueError("maxsize must be >= 1 and ttl must be > 0")

    def decorator(func: Callable[P, R]) -> Cached[P, R]:
        entries: OrderedDict[Hashable, tuple[float, R]] = OrderedDict()
        lock = threading.Lock()
        hits = misses = 0

        def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Hashable:
            return (args, tuple(sorted(kwargs.items())))

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal hits, misses
            key = make_key(args, kwargs)  # raises TypeError for unhashable arguments
            now = clock()
            with lock:
                item = entries.get(key)
                if item is not None:
                    stored_at, value = item
                    if now - stored_at < ttl:
                        entries.move_to_end(key)
                        hits += 1
                        return value
                    del entries[key]  # expired
                misses += 1
            value = func(*args, **kwargs)  # computed outside the lock
            with lock:
                entries[key] = (clock(), value)
                entries.move_to_end(key)
                while len(entries) > maxsize:
                    entries.popitem(last=False)
            return value

        def cache_info() -> CacheInfo:
            with lock:
                return CacheInfo(hits, misses, maxsize, len(entries))

        def cache_clear() -> None:
            nonlocal hits, misses
            with lock:
                entries.clear()
                hits = misses = 0

        wrapper.cache_info = cache_info  # type: ignore[attr-defined]
        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
