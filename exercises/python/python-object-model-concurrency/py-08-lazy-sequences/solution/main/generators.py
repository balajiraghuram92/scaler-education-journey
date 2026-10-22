"""
generators.py

Implement a generator function called even_numbers.

even_numbers(limit) should produce even numbers starting at 0.
It should stop before it reaches limit.
"""


def even_numbers(limit):
    if type(limit) is not int:
        raise TypeError("limit must be an integer")

    if limit < 0:
        raise ValueError("limit must not be negative")

    number = 0
    while number < limit:
        yield number
        number += 2
