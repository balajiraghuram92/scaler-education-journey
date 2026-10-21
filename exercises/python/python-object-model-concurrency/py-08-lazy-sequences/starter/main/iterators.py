"""
iterators.py

Implement a custom iterator class called NumberRange.

NumberRange(start, end) should work like a simple version of range().
It should produce numbers from start up to, but not including, end.
"""

from main.base import LazySequence


class NumberRange(LazySequence):
    """A lazy iterator over ``start`` (inclusive) to ``end`` (exclusive).

    - ``TypeError("start and end must both be integers")`` if either bound is not an ``int``
      (``bool``, ``float``, ``str`` and ``None`` are rejected)
    - ``ValueError("start must be less than end")`` if ``start >= end``
    - ``__iter__`` returns ``self``; ``__next__`` returns the next number or raises ``StopIteration``
    - after one full loop the object is exhausted: a second loop yields nothing
    - never build a list of the values
    """

    def __init__(self, start, end):
        raise NotImplementedError("Validate the bounds and store the iteration state")

    def __iter__(self):
        raise NotImplementedError("Implement __iter__")

    def __next__(self):
        raise NotImplementedError("Implement __next__")
