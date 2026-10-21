import sys

import pytest

from leakprobe import LeakProbe, deep_sizeof


class Plain:
    def __init__(self, a: object, b: object, c: object) -> None:
        self.a, self.b, self.c = a, b, c


class Slotted:
    __slots__ = ("a", "b", "c")

    def __init__(self, a: object, b: object, c: object) -> None:
        self.a, self.b, self.c = a, b, c


def test_deep_is_larger_than_shallow() -> None:
    records = [{"id": i, "text": "x" * 50} for i in range(100)]
    assert deep_sizeof(records) > 20 * sys.getsizeof(records)


def test_shared_objects_counted_once() -> None:
    big = "y" * 10_000
    once = deep_sizeof([big])
    twice = deep_sizeof([big, big])
    extra = twice - once
    assert 0 < extra < 100, f"the second reference should cost one pointer slot, not another 10 KB string (got {extra})"


def test_slots_instance_smaller_than_dict_instance() -> None:
    vals = ("a" * 40, "b" * 40, "c" * 40)
    assert deep_sizeof(Slotted(*vals)) < deep_sizeof(Plain(*vals))


def test_slotted_values_are_followed() -> None:
    small = deep_sizeof(Slotted(1, 1, 1))
    large = deep_sizeof(Slotted("z" * 5_000, 1, 1))
    assert large - small > 4_000


def test_cycles_terminate() -> None:
    a: list[object] = []
    a.append(a)
    assert deep_sizeof(a) == sys.getsizeof(a)


def test_probe_reports_released_and_retained() -> None:
    probe = LeakProbe()
    kept = [probe.track(Plain(1, 2, 3)) for _ in range(2)]
    probe.track(Plain(4, 5, 6))  # no strong reference kept
    assert probe.alive_count() == 2
    del kept
    assert probe.alive_count() == 0


class Base:
    __slots__ = ("base_value",)


class Child(Base):
    __slots__ = ("child_value", "never_set")

    def __init__(self, base_value: object, child_value: object) -> None:
        self.base_value = base_value
        self.child_value = child_value


def test_inherited_slots_are_followed_and_unset_slots_do_not_raise() -> None:
    small = deep_sizeof(Child(1, 1))
    big_base = deep_sizeof(Child("b" * 5_000, 1))
    big_child = deep_sizeof(Child(1, "c" * 5_000))
    assert big_base - small > 4_000, "slot declared on a base class was not followed"
    assert big_child - small > 4_000, "slot declared on the subclass was not followed"


def test_very_deep_structure_does_not_hit_the_recursion_limit() -> None:
    node = None
    for i in range(10_000):
        node = Plain(i, node, None)
    assert deep_sizeof(node) > 10_000 * 48, "all 10,000 nodes should be counted"


def test_does_not_descend_into_classes_or_functions() -> None:
    class Tagged:
        def __init__(self) -> None:
            self.kind = Plain  # a class reference
            self.fn = len  # a builtin
            self.helper = deep_sizeof  # a function

    size = deep_sizeof(Tagged())
    assert size < 2_000, f"instance data only, not the class/function graph (got {size} bytes)"


def test_track_returns_the_same_object_without_keeping_it_alive() -> None:
    probe = LeakProbe()
    obj = Plain(1, 2, 3)
    assert probe.track(obj) is obj
    assert probe.alive_count() == 1
    del obj
    assert probe.alive_count() == 0
