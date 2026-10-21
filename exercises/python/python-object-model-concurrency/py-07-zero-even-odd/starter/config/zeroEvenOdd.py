class PrintNumber:
    """Provided helper. Use it as is: output must go through ``printNumber.accept(x)``."""

    def accept(self, x):
        print(x, end='')


class ZeroEvenOdd:
    """Three threads together print ``0`` before every number from 1 to ``n`` (``n = 5`` gives ``0102030405``).

    - ``zero(printNumber)`` prints ``0`` exactly ``n`` times
    - ``odd(printNumber)`` prints the odd numbers ``1, 3, 5, ...`` up to ``n``
    - ``even(printNumber)`` prints the even numbers ``2, 4, ...`` up to ``n``
    - each method runs in its own thread, started in any order
    - coordinate with ``threading.Semaphore`` only: no sleeping, no polling
    - ``n = 1`` (no ``even`` work) must not deadlock
    """

    def __init__(self, n):
        raise NotImplementedError("Store n and create the semaphores")

    def zero(self, printNumber):
        raise NotImplementedError("Implement zero")

    def even(self, printNumber):
        raise NotImplementedError("Implement even")

    def odd(self, printNumber):
        raise NotImplementedError("Implement odd")
