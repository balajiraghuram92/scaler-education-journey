import inspect
from itertools import islice

import pytest

from main.base import LazySequence
from main.generators import even_numbers
from main.iterators import NumberRange


def test_number_range_yields_start_up_to_but_not_including_end():
    assert list(NumberRange(3, 8)) == [3, 4, 5, 6, 7]
    assert list(NumberRange(-2, 2)) == [-2, -1, 0, 1]
    assert list(NumberRange(5, 6)) == [5], "a one-element range"


def test_number_range_is_a_lazy_sequence_and_its_own_iterator():
    r = NumberRange(0, 3)
    assert isinstance(r, LazySequence), "NumberRange must inherit from LazySequence"
    assert iter(r) is r, "__iter__ must return self"
    assert next(r) == 0 and next(r) == 1 and next(r) == 2
    with pytest.raises(StopIteration):
        next(r)


def test_number_range_is_exhausted_after_one_loop():
    r = NumberRange(0, 4)
    assert list(r) == [0, 1, 2, 3]
    assert list(r) == [], "a second loop over the same object yields nothing"


def test_number_range_is_lazy_for_huge_ranges():
    r = NumberRange(0, 10**15)
    assert list(islice(r, 3)) == [0, 1, 2], "must produce values on demand without building a list"
    assert next(r) == 3


@pytest.mark.parametrize("start,end", [(1.5, 3), (1, "3"), (None, 3), (1, None), (True, 3), (0, True), ("a", "b")])
def test_number_range_rejects_non_integer_bounds(start, end):
    with pytest.raises(TypeError) as info:
        NumberRange(start, end)
    assert str(info.value) == "start and end must both be integers"


@pytest.mark.parametrize("start,end", [(5, 5), (6, 5), (0, -1)])
def test_number_range_rejects_start_not_less_than_end(start, end):
    with pytest.raises(ValueError) as info:
        NumberRange(start, end)
    assert str(info.value) == "start must be less than end"


def test_base_class_is_abstract_and_unchanged():
    with pytest.raises(TypeError):
        LazySequence()
    assert LazySequence.__abstractmethods__ == frozenset({"__iter__", "__next__"})


def test_even_numbers_values_and_boundaries():
    assert list(even_numbers(10)) == [0, 2, 4, 6, 8], "limit itself is excluded"
    assert list(even_numbers(7)) == [0, 2, 4, 6]
    assert list(even_numbers(1)) == [0]
    assert list(even_numbers(0)) == [], "limit 0 yields nothing"


def test_even_numbers_is_a_lazy_generator():
    assert inspect.isgeneratorfunction(even_numbers), "even_numbers must be a generator function (use yield)"
    gen = even_numbers(10**15)
    assert next(gen) == 0
    assert list(islice(gen, 3)) == [2, 4, 6], "values are produced on demand"


@pytest.mark.parametrize("bad", [1.5, "4", None, True])
def test_even_numbers_rejects_non_integer_limit(bad):
    with pytest.raises(TypeError) as info:
        list(even_numbers(bad))
    assert str(info.value) == "limit must be an integer"


def test_even_numbers_rejects_negative_limit():
    with pytest.raises(ValueError) as info:
        list(even_numbers(-1))
    assert str(info.value) == "limit must not be negative"
