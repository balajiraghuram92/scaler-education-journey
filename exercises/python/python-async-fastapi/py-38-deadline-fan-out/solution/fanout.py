import asyncio
from collections.abc import Callable, Coroutine, Sequence
from typing import Any


async def fan_out[T](
    factories: Sequence[Callable[[], Coroutine[Any, Any, T]]],
    *,
    timeout: float,
) -> list[T]:
    """Run every call concurrently and return results in input order.

    One failure cancels the siblings and surfaces as an ExceptionGroup.
    If the deadline passes first, everything is cancelled and TimeoutError is raised.
    """
    async with asyncio.timeout(timeout):
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(make()) for make in factories]
    return [task.result() for task in tasks]
