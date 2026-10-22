class FooBar:
    """Two threads share one ``FooBar(n)``; the combined output must be ``foobar`` repeated ``n`` times.

    One thread calls ``foo()`` and another calls ``bar()``, in any start order.

    Requirements:
    - ``__init__(n)`` stores ``n`` and creates the semaphores
    - ``foo()`` loops ``n`` times and prints ``foo`` with ``end=''``
    - ``bar()`` loops ``n`` times and prints ``bar`` with ``end=''``
    - the first print is always ``foo`` and the prints strictly alternate
    - use ``threading.Semaphore``: no sleep, no polling, no shared boolean
    - must work for ``n = 0`` and ``n = 1``
    """

    def __init__(self, n):
        raise NotImplementedError("Store n and create the semaphores")

    def foo(self):
        raise NotImplementedError("Implement foo")

    def bar(self):
        raise NotImplementedError("Implement bar")
