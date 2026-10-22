import asyncio
from collections.abc import Awaitable, Callable, Iterable


async def bounded_map[T, R](
    func: Callable[[T], Awaitable[R]],
    items: Iterable[T],
    *,
    workers: int,
    queue_size: int | None = None,
) -> list[R]:
    """Apply ``func`` to every item with exactly ``workers`` worker tasks.

    Requirements:
    - items are pulled lazily from ``items`` (it may be a generator) through a bounded
      ``asyncio.Queue``: ``maxsize = workers`` when ``queue_size`` is None, else ``queue_size``
    - the producer suspends when the queue is full (backpressure)
    - results are returned in input order; an empty iterable returns ``[]``
    - stop the workers with one ``None`` sentinel per worker (do not use ``Queue.shutdown``)
    - the first failure cancels the other workers and the producer (even one blocked in
      ``put``) and surfaces as an ``ExceptionGroup``; it must never deadlock
    - ``workers < 1`` or ``queue_size < 1`` raises ``ValueError``
    - use ``asyncio.TaskGroup``; do not use ``asyncio.gather``
    """
    raise NotImplementedError("Implement bounded_map")
