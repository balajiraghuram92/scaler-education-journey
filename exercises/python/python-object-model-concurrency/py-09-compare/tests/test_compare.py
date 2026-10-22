import typing
from typing import TypeVar

import pytest

from config.compare import compare


def test_direct_comparison_of_numbers_and_strings():
    assert compare(5, 10) == -1
    assert compare(20, 10) == 1
    assert compare("abc", "abc") == 0
    assert compare("apple", "banana") == -1
    assert compare(2.5, 2.5) == 0


def test_returns_only_minus_one_zero_or_one():
    for x, y, expected in [(5, 100, -1), (100, 5, 1), (7, 7, 0)]:
        result = compare(x, y)
        assert type(result) is int, "return an int, not a bool or a difference"
        assert result == expected, f"compare({x}, {y}) should be {expected}, not the numeric difference"


def test_comparison_with_key_function():
    alice = {"name": "Alice", "age": 25}
    bob = {"name": "Bob", "age": 30}
    assert compare(alice, bob, key=lambda s: s["age"]) == -1
    assert compare(bob, alice, key=lambda s: s["age"]) == 1
    assert compare(alice, {"name": "Zed", "age": 25}, key=lambda s: s["age"]) == 0
    assert compare("apple", "fig", key=len) == 1
    assert compare("abc", "xyz", key=len) == 0, "equal keys compare as equal even if the objects differ"


def test_key_is_called_exactly_once_per_argument():
    seen = []

    def key(value):
        seen.append(value)
        return value * 2

    assert compare(3, 8, key=key) == -1
    assert seen == [3, 8], "key(x) and key(y) must each be computed exactly once"


def test_none_key_uses_direct_comparison_but_falsy_key_is_still_used():
    assert compare(1, 2, key=None) == -1

    class FalsyNegate:
        def __bool__(self):
            return False

        def __call__(self, value):
            return -value

    assert compare(1, 2, key=FalsyNegate()) == 1, "test `key is not None`, not truthiness: a falsy callable is still a key"


def test_works_with_objects_defining_only_lt_and_eq():
    class Version:
        def __init__(self, n):
            self.n = n

        def __lt__(self, other):
            return self.n < other.n

        def __eq__(self, other):
            return self.n == other.n

        __hash__ = None

    assert compare(Version(1), Version(2)) == -1
    assert compare(Version(2), Version(2)) == 0
    assert compare(Version(3), Version(2)) == 1


def test_does_not_modify_or_sort_arguments():
    a, b = [3, 1, 2], [1, 2, 3]
    assert compare(a, b) == 1
    assert a == [3, 1, 2] and b == [1, 2, 3], "arguments must be left untouched"


def test_signature_uses_a_shared_typevar_and_typing_any():
    hints = typing.get_type_hints(compare)
    assert isinstance(hints.get("x"), TypeVar), "annotate x with a TypeVar"
    assert hints["x"] is hints.get("y"), "x and y must share the same TypeVar"
    assert hints.get("return") is int, "annotate the return type as int"
    assert "built-in function any" not in str(hints.get("key")), "use typing.Any, not the builtin any()"
    assert "typing.Any" in str(hints.get("key")), "key should be Callable[[T], Any]"
    assert type(None) in typing.get_args(hints.get("key")), "key should be optional: ... | None"
