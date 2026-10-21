import threading

import pytest

from lazy import lazy


class Report:
    def __init__(self) -> None:
        self.calls = 0

    @lazy
    def total(self) -> int:
        self.calls += 1
        return 42

    @lazy
    def flaky(self) -> int:
        self.calls += 1
        if self.calls < 3:
            raise RuntimeError("not yet")
        return self.calls


def test_computed_once_and_cached_in_dict() -> None:
    r = Report()
    assert r.total == 42 and r.total == 42
    assert r.calls == 1
    assert r.__dict__["total"] == 42


def test_per_instance_isolation() -> None:
    a, b = Report(), Report()
    a.total
    assert a.calls == 1 and b.calls == 0


def test_class_access_returns_descriptor() -> None:
    assert isinstance(Report.total, lazy)
    assert Report.total.attrname == "total"


def test_delete_invalidates_and_assignment_overrides() -> None:
    r = Report()
    r.total
    del r.total
    r.total
    assert r.calls == 2
    r.total = 7  # non-data descriptor: plain assignment wins
    assert r.total == 7


def test_exceptions_are_not_cached() -> None:
    r = Report()
    for _ in range(2):
        with pytest.raises(RuntimeError):
            r.flaky
    assert r.flaky == 3


def test_threads_compute_once() -> None:
    r = Report()
    barrier = threading.Barrier(8)
    results: list[int] = []

    def worker() -> None:
        barrier.wait()
        results.append(r.total)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert results == [42] * 8
    assert r.calls == 1


def test_same_descriptor_under_two_names_is_rejected() -> None:
    with pytest.raises(TypeError, match="two names"):
        class Bad:
            @lazy
            def a(self) -> int:
                return 1

            b = a


class Nullable:
    def __init__(self) -> None:
        self.calls = 0

    @lazy
    def nothing(self) -> None:
        self.calls += 1
        return None

    @lazy
    def other(self) -> str:
        return "other"


class Sub(Nullable):
    pass


def test_none_result_is_cached() -> None:
    n = Nullable()
    assert n.nothing is None and n.nothing is None
    assert n.calls == 1, "None is a valid cached value, not a cache miss"


def test_attributes_cached_independently_and_inherited() -> None:
    s = Sub()
    assert s.other == "other"
    assert "other" in s.__dict__ and "nothing" not in s.__dict__
    assert isinstance(Sub.other, lazy)
