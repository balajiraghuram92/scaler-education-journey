import pytest

from pool import Driver, DriverPool


def make():
    return DriverPool([Driver("D1", "a", 4.0), Driver("D2", "b", 4.5), Driver("D1", "dup", 1.0)])


def ids(pool):
    return [d.driver_id for d in pool]


def test_driver_identity_is_the_id_and_hash_survives_rating_change():
    a, b = Driver("D1", "Ramesh", 4.8), Driver("D1", "Ramesh K", 3.0)
    assert a == b and hash(a) == hash(b), "drivers with the same ID are equal and hash equal"
    assert len({a, b}) == 1, "equal drivers collapse in a set"
    assert a != Driver("D2", "Ramesh", 4.8)
    bucket = {a}
    a.rating = 1.0
    assert a in bucket, "changing rating must not change the hash"


def test_driver_compares_politely_with_foreign_types():
    d = Driver("D1", "x", 5)
    assert (d == "D1") is False, "== with a non-driver is False, not an error"
    assert d.__eq__("D1") is NotImplemented, "__eq__ must return NotImplemented for non-drivers"


def test_driver_id_is_read_only_but_other_fields_are_plain():
    d = Driver("D1", "x", 4.0)
    with pytest.raises(AttributeError):
        d.driver_id = "D2"
    d.name, d.rating = "y", 3.5
    assert (d.name, d.rating, d.driver_id) == ("y", 3.5, "D1")


def test_reprs():
    assert repr(Driver("D1", "Ramesh", 4.8)) == "Driver('D1', 'Ramesh', 4.8)"
    assert repr(DriverPool([Driver("D1", "a", 4.0)])) == "DriverPool([Driver('D1', 'a', 4.0)])"
    assert repr(DriverPool()) == "DriverPool([])"


def test_pool_dedupes_keeping_first_and_preserves_order():
    p = make()
    assert len(p) == 2
    assert p[0].name == "a", "the FIRST driver for each ID is kept"
    assert ids(DriverPool([Driver("B", "", 1), Driver("A", "", 1), Driver("B", "", 1)])) == ["B", "A"]


def test_pool_truthiness_len_and_repeatable_iteration():
    p = make()
    assert p and not DriverPool(), "an empty pool is falsy"
    assert "__bool__" not in vars(DriverPool), "rely on __len__, do not define __bool__"
    assert ids(p) == ["D1", "D2"]
    assert ids(p) == ["D1", "D2"], "iterating twice must give the same result"
    it1, it2 = iter(p), iter(p)
    assert it1 is not it2, "every iter() call returns a fresh iterator"


def test_pool_indexing_and_slicing_returns_pool():
    p = make()
    assert p[-1].driver_id == "D2" and isinstance(p[0], Driver)
    s = p[:1]
    assert isinstance(s, DriverPool) and ids(s) == ["D1"], "a slice returns a new DriverPool"
    assert s is not p and len(p) == 2, "slicing must not change the original"
    assert len(p[5:]) == 0 and isinstance(p[5:], DriverPool)
    with pytest.raises(IndexError):
        p[5]


def test_pool_contains_driver_or_id():
    p = make()
    assert "D2" in p and Driver("D2", "zzz", 0) in p
    assert "D9" not in p and Driver("D9", "n", 1) not in p
    assert 42 not in p, "unrelated types are simply not members"


def test_pool_add_unions_and_rejects_foreign_types():
    p = make() + DriverPool([Driver("D3", "c", 3.0), Driver("D2", "again", 2.0)])
    assert ids(p) == ["D1", "D2", "D3"], "union keeps order and the first driver per ID"
    assert p[1].name == "b"
    assert make().__add__([Driver("D9", "x", 1)]) is NotImplemented
    with pytest.raises(TypeError):
        make() + [Driver("D9", "x", 1)]


def test_pool_is_independent_of_its_input_and_accepts_any_iterable():
    source = [Driver("D1", "a", 4.0)]
    p = DriverPool(source)
    source.append(Driver("D2", "b", 1.0))
    assert len(p) == 1, "the pool must not share the caller's list"
    assert ids(DriverPool(d for d in [Driver("G1", "", 1), Driver("G2", "", 1)])) == ["G1", "G2"], "generators are fine"
    assert not issubclass(DriverPool, list), "do not subclass list"
