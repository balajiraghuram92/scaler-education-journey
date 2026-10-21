import queue
import threading
from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


class SafeCounter:
    """A counter whose read-modify-write is one critical section."""

    def __init__(self, start: int = 0) -> None:
        self._value = start
        self._lock = threading.Lock()

    def incr(self, delta: int = 1) -> int:
        with self._lock:
            self._value += delta
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


def threaded_map(fn: Callable[[T], R], items: Sequence[T], *, workers: int = 4) -> list[R]:
    """Apply fn to every item using plain threads; results keep input order.

    All items are attempted. If any call raised, an ExceptionGroup holding every
    failure (ordered by input index) is raised after all workers have finished.
    """
    if workers < 1:
        raise ValueError("workers must be >= 1")
    n = len(items)
    if n == 0:
        return []

    tasks: queue.Queue[int] = queue.Queue()
    for i in range(n):
        tasks.put(i)

    results: list[R | None] = [None] * n
    errors: dict[int, Exception] = {}
    errors_lock = threading.Lock()

    def worker() -> None:
        while True:
            try:
                i = tasks.get_nowait()
            except queue.Empty:
                return
            try:
                results[i] = fn(items[i])            # each index is written by one thread only
            except Exception as exc:
                with errors_lock:
                    errors[i] = exc

    threads = [threading.Thread(target=worker, name=f"tmap-{k}") for k in range(min(workers, n))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if errors:
        raise ExceptionGroup("threaded_map failed", [errors[i] for i in sorted(errors)])
    return results  # type: ignore[return-value]
