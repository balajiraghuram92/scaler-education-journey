import asyncio
from collections.abc import Awaitable, Callable, Iterable


async def bounded_map[T, R](
    func: Callable[[T], Awaitable[R]],
    items: Iterable[T],
    *,
    workers: int,
    queue_size: int | None = None,
) -> list[R]:
    """Apply `func` to every item with exactly `workers` worker tasks.

    Items are pulled lazily from `items` through a bounded queue, so memory stays
    O(workers + queue_size) however long the iterable is. Results keep input order.
    The first failure cancels everything and surfaces as an ExceptionGroup.
    """
    if workers < 1:
        raise ValueError("workers must be >= 1")
    size = workers if queue_size is None else queue_size
    if size < 1:
        raise ValueError("queue_size must be >= 1")

    queue: asyncio.Queue[tuple[int, T] | None] = asyncio.Queue(maxsize=size)
    results: dict[int, R] = {}

    async def worker() -> None:
        while (job := await queue.get()) is not None:
            index, item = job
            results[index] = await func(item)

    count = 0
    async with asyncio.TaskGroup() as tg:
        for _ in range(workers):
            tg.create_task(worker())
        for index, item in enumerate(items):
            await queue.put((index, item))  # blocks when workers fall behind
            count += 1
        for _ in range(workers):
            await queue.put(None)  # one stop signal per worker
    return [results[i] for i in range(count)]
