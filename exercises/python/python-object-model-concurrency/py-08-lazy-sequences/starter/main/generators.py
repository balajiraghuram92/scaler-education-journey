"""
generators.py

Implement a generator function called even_numbers.

even_numbers(limit) should produce even numbers starting at 0.
It should stop before it reaches limit.
"""


def even_numbers(limit):
    """Yield 0, 2, 4, ... strictly below ``limit``, one at a time.

    - must be a generator function (use ``yield``); do not build a list
    - ``TypeError("limit must be an integer")`` for a non-int, including ``bool``
    - ``ValueError("limit must not be negative")`` for a negative limit
    - because this is a generator, the errors surface on the first ``next()``
    """
    raise NotImplementedError("Implement even_numbers")
