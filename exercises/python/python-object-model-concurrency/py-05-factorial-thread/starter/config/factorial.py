import math  # noqa: F401
import threading


class FactorialThread(threading.Thread):
    """A worker thread that computes ``n!``.

    - ``__init__(self, n)`` calls ``super().__init__()``, stores ``n`` and sets ``self.result = None``
    - ``run()`` computes ``math.factorial(self.n)`` and stores it in ``self.result``
    """

    def __init__(self, n):
        raise NotImplementedError("Implement FactorialThread.__init__")

    def run(self):
        raise NotImplementedError("Implement FactorialThread.run")


def compute_large_factorial(n):
    """Create a ``FactorialThread``, start it, ``join()`` it, and return ``thread.result``."""
    raise NotImplementedError("Implement compute_large_factorial")
