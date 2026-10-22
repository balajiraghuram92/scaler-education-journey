class Foo:
    """Three methods run by three different threads, in any order, must still run in order.

    ``first()``, ``second()`` and ``third()`` must append ``"first"``, ``"second"`` and ``"third"``
    to ``self.output`` in exactly that order, whatever order the threads start in.

    Requirements:
    - create every semaphore you need, and the ``output`` list, in ``__init__``
    - ``first`` appends and then signals ``second``; ``second`` waits, appends, signals ``third``;
      ``third`` waits and appends
    - no sleeping, no busy waiting, no shared flags
    """

    def __init__(self):
        raise NotImplementedError("Create the semaphores and the output list")

    def first(self):
        raise NotImplementedError("Implement first")

    def second(self):
        raise NotImplementedError("Implement second")

    def third(self):
        raise NotImplementedError("Implement third")
