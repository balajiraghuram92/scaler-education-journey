class Counter:
    """A counter that is safe to update from many threads.

    ``__init__(initial_count)`` stores the starting value and creates a ``threading.Lock``.
    Every method that reads or writes the value must hold that lock (``with self._lock:``).
    """

    def __init__(self, initial_count):
        raise NotImplementedError("Store the count and create the lock")

    def incValue(self, offset):
        """Add ``offset`` to the counter."""
        raise NotImplementedError("Implement incValue")

    def getValue(self):
        """Return the current value."""
        raise NotImplementedError("Implement getValue")

    def decValue(self, offset):
        """Subtract ``offset`` from the counter."""
        raise NotImplementedError("Implement decValue")


def concurrent_inc(counter, offset):
    """Call ``counter.incValue(offset)`` 1000 times (meant to run inside a thread)."""
    raise NotImplementedError("Implement concurrent_inc")


def concurrent_dec(counter, offset):
    """Call ``counter.decValue(offset)`` 1000 times (meant to run inside a thread)."""
    raise NotImplementedError("Implement concurrent_dec")
