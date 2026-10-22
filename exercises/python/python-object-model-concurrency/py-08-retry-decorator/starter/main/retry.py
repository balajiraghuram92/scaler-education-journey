"""
retry.py

Implement a decorator called retry that automatically retries a function
if it raises an exception, instead of failing immediately.
"""

import functools
import time


def retry(times, delay=0):
    """Return a decorator that retries a function when it raises an exception.

    Args:
        times (int): total number of attempts. Must be a positive ``int`` (not a ``bool``,
            float, str or None), otherwise raise ``ValueError("times must be a positive integer")``.
        delay (int or float): seconds to wait between failed attempts. Must be a non-negative
            ``int`` or ``float`` (not a ``bool`` or None), otherwise raise
            ``ValueError("delay must be non-negative")``.

    Rules:
    - validate the arguments when ``retry(...)`` is called, not when the decorated function is called
    - call the function up to ``times`` times; return the first successful result immediately
    - between failed attempts (not after the last) call ``time.sleep(delay)``
    - if every attempt fails, raise ``RuntimeError(f"Function failed after {times} attempts")``
      with ``raise ... from e`` so ``__cause__`` is the last exception
    - forward ``*args`` and ``**kwargs`` unchanged and preserve ``__name__`` / ``__doc__``
    """
    raise NotImplementedError("Implement retry")
