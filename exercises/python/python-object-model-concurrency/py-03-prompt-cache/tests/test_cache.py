import pytest

from cache import PromptKey, ResponseCache


def key(text="hi", model="m1", t=0.0):
    return PromptKey(model, t, [{"role": "user", "content": text}])


def test_equal_keys_hash_equal_even_with_different_dict_order():
    a = PromptKey("m", 0.0, [{"role": "user", "content": "x"}])
    b = PromptKey("m", 0.0, [{"content": "x", "role": "user"}])
    assert a == b and hash(a) == hash(b), "key order inside a message must not matter"
    assert a.messages == ((("content", "x"), ("role", "user")),), "messages become a tuple of tuples of sorted items"
    assert key(model="m1") != key(model="m2") and key(t=0.0) != key(t=0.7), "model and temperature are part of the key"
    assert len({a, b}) == 1


def test_key_is_isolated_from_caller_mutation():
    msgs = [{"role": "user", "content": "x"}]
    k = PromptKey("m", 0.0, msgs)
    h = hash(k)
    msgs.append({"role": "system", "content": "y"})
    msgs[0]["content"] = "changed"
    assert hash(k) == h, "mutating the caller's data must not change the hash"
    assert k == PromptKey("m", 0.0, [{"role": "user", "content": "x"}]), "...or the equality"


def test_key_is_immutable_and_rejects_foreign_comparison():
    k = key()
    for attr in ("model", "temperature", "messages"):
        with pytest.raises(AttributeError):
            setattr(k, attr, "other")
    assert (k == "hi") is False, "== with another type is False"
    assert k.__eq__("hi") is NotImplemented, "__eq__ must return NotImplemented for other types"


def test_lru_eviction_order_and_recency_from_reads():
    c = ResponseCache(2)
    c[key("a")] = "A"
    c[key("b")] = "B"
    assert c[key("a")] == "A"          # a is now most recent
    c[key("c")] = "C"                  # evicts b
    assert key("b") not in c, "b was least recently used and must be evicted"
    assert key("a") in c and key("c") in c and len(c) == 2


def test_overwriting_a_key_refreshes_it_without_evicting():
    c = ResponseCache(2)
    c[key("a")] = "A"
    c[key("b")] = "B"
    c[key("a")] = "A2"                 # refresh a, size stays 2
    assert len(c) == 2 and c[key("b")] == "B", "overwriting an existing key must not evict anything"
    c[key("b")] = "B2"
    c[key("c")] = "C"                  # a is now the least recently used
    assert key("a") not in c and c[key("b")] == "B2" and c[key("c")] == "C"
    tiny = ResponseCache(1)
    tiny[key("x")], tiny[key("y")] = "X", "Y"
    assert list(tiny) == [key("y")], "capacity 1 keeps only the latest key"


def test_mapping_methods_come_for_free():
    assert {"get", "pop", "update", "items"}.isdisjoint(vars(ResponseCache)), "inherit these from MutableMapping"
    c = ResponseCache(3)
    assert c.get(key("zz"), "miss") == "miss"
    c.update({key("a"): "A"})
    assert list(c.items()) == [(key("a"), "A")]
    assert c.pop(key("a")) == "A" and not c
    with pytest.raises(KeyError):
        c[key("never")]
    with pytest.raises(KeyError):
        del c[key("never")]


def test_iteration_is_a_snapshot():
    c = ResponseCache(3)
    c[key("a")] = "A"
    c[key("b")] = "B"
    for k in c:
        c[k]                              # reading reorders the cache; must not break the loop
    assert len(c) == 2
    seen = [k for k in c if c.pop(k)]     # deleting while iterating must not break either
    assert len(seen) == 2 and len(c) == 0


def test_invalid_capacity():
    for bad in (0, -1):
        with pytest.raises(ValueError):
            ResponseCache(bad)
    assert len(ResponseCache(1)) == 0


def test_transaction_commits_on_success():
    c = ResponseCache(5)
    with c.transaction() as tx:
        tx.put(key("a"), "A")
        tx.put(key("b"), "B")
        tx.put(key("a"), "A2")
        assert key("a") not in c and len(c) == 0, "writes are buffered until the block exits"
    assert c[key("a")] == "A2" and c[key("b")] == "B", "all buffered writes are committed, the last put wins"
    small = ResponseCache(2)
    with small.transaction() as tx:
        for t in ("a", "b", "c"):
            tx.put(key(t), t.upper())
    assert len(small) == 2 and key("a") not in small, "committing goes through the normal LRU path"


def test_transaction_discards_on_error_and_does_not_swallow():
    c = ResponseCache(5)
    c[key("keep")] = "K"
    with pytest.raises(RuntimeError, match="boom"):
        with c.transaction() as tx:
            tx.put(key("a"), "A")
            raise RuntimeError("boom")
    assert list(c) == [key("keep")], "nothing from the failed block may be stored"
    tx2 = c.transaction()
    assert not tx2.__exit__(ValueError, ValueError("x"), None), "__exit__ must return a falsy value"
