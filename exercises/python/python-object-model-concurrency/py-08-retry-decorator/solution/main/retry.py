"""
retry.py

Implement a decorator called retry that automatically retries a function
if it raises an exception, instead of failing immediately.
"""

import functools
import time


def retry(times, delay=0):
    """
    Return a decorator that retries a function when it raises an exception.

    Args:
        times (int): How many total attempts to make. Must be a positive integer.
        delay (int or float): Seconds to wait between attempts. Must not be negative.
    """

    if type(times) is not int or times <= 0:
        raise ValueError("times must be a positive integer")

    if type(delay) not in (int, float) or delay < 0:
        raise ValueError("delay must be non-negative")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt_number in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt_number == times:
                        raise RuntimeError(
                            f"Function failed after {times} attempts"
                        ) from e

                    time.sleep(delay)

        return wrapper

    return decorator
