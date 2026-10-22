"""
iterators.py

Implement a custom iterator class called NumberRange.

NumberRange(start, end) should work like a simple version of range().
It should produce numbers from start up to, but not including, end.
"""

from main.base import LazySequence


class NumberRange(LazySequence):
    def __init__(self, start, end):
        if type(start) is not int or type(end) is not int:
            raise TypeError("start and end must both be integers")

        if start >= end:
            raise ValueError("start must be less than end")

        self.current = start
        self.end = end

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration

        number = self.current
        self.current += 1
        return number
