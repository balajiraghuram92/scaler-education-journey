import threading

import pytest

from lru import CacheStats, LRUCache


@pytest.mark.parametrize("capacity", [0, -3], ids=["zero", "negative"])
def test_capacity_must_be_positive(capacity):
    with pytest.raises(ValueError, match="capacity must be >= 1"):
        LRUCache[str, int](capacity)


def test_evicts_least_recently_used():
    cache = LRUCache[str, int](2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert "b" not in cache, "b was least recently used and must be evicted"
    assert "a" in cache and "c" in cache
    assert len(cache) == 2


def test_put_existing_key_updates_value_and_recency_without_eviction():
    cache = LRUCache[str, int](2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 10)
    assert len(cache) == 2 and cache.stats().evictions == 0, "updating must not evict"
    cache.put("c", 3)
    assert cache.get("a") == 10, "a was refreshed by the update"
    assert cache.get("b") is None


def test_capacity_one_and_eviction_count():
    cache = LRUCache[int, str](1)
    cache.put(1, "x")
    cache.put(2, "y")
    cache.put(3, "z")
    assert cache.get(1) is None
    assert cache.get(3) == "z"
    assert cache.stats().evictions == 2


def test_contains_does_not_change_recency():
    cache = LRUCache[str, int](2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert "a" in cache
    cache.put("c", 3)
    assert "a" not in cache, "membership test must not refresh recency"
    assert cache.stats().hits == 0 and cache.stats().misses == 0, "membership is not a hit or miss"


def test_get_returns_default_and_stats_are_frozen():
    cache = LRUCache[str, int](2)
    assert cache.get("missing", 42) == 42
    assert cache.get("missing") is None
    cache.put("a", 1)
    cache.get("a")
    stats = cache.stats()
    assert stats == CacheStats(hits=1, misses=2, evictions=0, size=1, capacity=2)
    with pytest.raises(AttributeError):
        stats.hits = 5


def test_get_or_set_calls_factory_once_and_does_not_cache_failures():
    cache = LRUCache[str, int](2)
    calls: list[str] = []

    def factory() -> int:
        calls.append("x")
        return 7

    assert cache.get_or_set("k", factory) == 7
    assert cache.get_or_set("k", factory) == 7
    assert calls == ["x"]

    def boom() -> int:
        raise RuntimeError("no")

    with pytest.raises(RuntimeError):
        cache.get_or_set("bad", boom)
    assert "bad" not in cache
    assert cache.get_or_set("bad", factory) == 7, "a failed factory is retried next time"


def test_get_or_set_refreshes_recency_and_counts_hits_and_misses():
    cache = LRUCache[str, int](2)
    cache.get_or_set("a", lambda: 1)
    cache.get_or_set("b", lambda: 2)
    cache.get_or_set("a", lambda: 99)
    cache.put("c", 3)
    assert "b" not in cache and "a" in cache, "a hit through get_or_set refreshes recency"
    stats = cache.stats()
    assert (stats.hits, stats.misses) == (1, 2)


def test_get_or_set_runs_factory_once_across_threads():
    cache = LRUCache[str, int](4)
    barrier = threading.Barrier(8)
    calls: list[int] = []
    results: list[int] = []

    def factory() -> int:
        calls.append(1)
        return 42

    def worker() -> None:
        barrier.wait(timeout=5)
        results.append(cache.get_or_set("shared", factory))

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(calls) == 1, "the factory must run at most once per missing key"
    assert results == [42] * 8


def test_size_never_exceeds_capacity_under_threads():
    cache = LRUCache[int, int](16)
    errors: list[BaseException] = []

    def hammer(offset: int) -> None:
        try:
            for i in range(1_000):
                cache.put((i + offset) % 100, i)
                cache.get((i * 7 + offset) % 100)
                assert len(cache) <= 16
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=hammer, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert errors == []
    assert len(cache) <= 16
    stats = cache.stats()
    assert stats.size == len(cache)
    assert stats.evictions > 0
