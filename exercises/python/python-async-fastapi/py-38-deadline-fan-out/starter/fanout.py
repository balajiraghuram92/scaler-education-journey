import asyncio
from collections.abc import Callable, Coroutine, Sequence
from typing import Any


async def fan_out[T](
    factories: Sequence[Callable[[], Coroutine[Any, Any, T]]],
    *,
    timeout: float,
) -> list[T]:
    """Run every call concurrently and return results in input order.

    Requirements:
    - each factory is a zero-argument callable returning a coroutine; call it only
      once you are inside the task group
    - use ``asyncio.TaskGroup`` and ``asyncio.timeout`` (not ``asyncio.gather``)
    - an empty sequence returns ``[]``
    - if a call raises, the siblings are cancelled (their ``finally`` blocks run before
      this function returns control) and the failure surfaces as an ``ExceptionGroup``
      that you do not unwrap
    - if the shared deadline passes first, every call is cancelled and ``TimeoutError``
      is raised
    """
    raise NotImplementedError("Implement fan_out")
