import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

ErrorHandler = Callable[[str, BaseException], None]


class TaskSupervisor:
    """Owns fire-and-forget tasks: strong references, error reporting, orderly shutdown."""

    def __init__(self, on_error: ErrorHandler) -> None:
        """``on_error(task_name, exc)`` is called once for every task that fails."""
        raise NotImplementedError("Implement __init__")

    @property
    def pending(self) -> int:
        """Number of tasks that have not finished yet."""
        raise NotImplementedError("Implement pending")

    def spawn(self, coro: Coroutine[Any, Any, Any], *, name: str) -> asyncio.Task[Any]:
        """Schedule ``coro`` as a named task and keep a strong reference to it.

        - the task removes itself when it finishes (``add_done_callback``)
        - after shutdown has started, close ``coro`` (so Python does not warn that it
          was never awaited) and raise ``RuntimeError``
        """
        raise NotImplementedError("Implement spawn")

    async def shutdown(self, grace: float) -> int:
        """Stop accepting work, give running tasks ``grace`` seconds, cancel the rest.

        Wait for the cancelled tasks to finish their cleanup, then return how many had
        to be cancelled. Calling it again returns ``0`` when nothing is left.
        A failed task is reported through ``on_error``; a cancelled one is not.
        """
        raise NotImplementedError("Implement shutdown")
