import queue  # noqa: F401
import threading  # noqa: F401
from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


class SafeCounter:
    """A counter whose read-modify-write is one critical section (protect it with a ``Lock``).

    - ``SafeCounter(start=0)``
    - ``incr(delta=1) -> int`` adds ``delta`` and returns the NEW value
    - ``value`` property returns the current value
    """

    def __init__(self, start: int = 0) -> None:
        raise NotImplementedError("Implement SafeCounter.__init__")

    def incr(self, delta: int = 1) -> int:
        raise NotImplementedError("Implement SafeCounter.incr")

    @property
    def value(self) -> int:
        raise NotImplementedError("Implement SafeCounter.value")


def threaded_map(fn: Callable[[T], R], items: Sequence[T], *, workers: int = 4) -> list[R]:
    """Apply ``fn`` to every item using plain threads; results keep INPUT order.

    - at most ``workers`` threads, and never more threads than items
    - ``workers < 1`` raises ``ValueError``; empty ``items`` returns ``[]`` without starting threads
    - distribute work through a ``queue.Queue`` of indices; workers stop when the queue is empty
      (no busy waiting, no sleeping)
    - if any call raises ``Exception``: keep processing the remaining items, join every thread, then raise
      ``ExceptionGroup("threaded_map failed", [...])`` with the exceptions ordered by input index
    """
    raise NotImplementedError("Implement threaded_map")
