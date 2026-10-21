import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

ErrorHandler = Callable[[str, BaseException], None]


class TaskSupervisor:
    """Owns fire-and-forget tasks: strong references, error reporting, orderly shutdown."""

    def __init__(self, on_error: ErrorHandler) -> None:
        self._on_error = on_error
        self._tasks: set[asyncio.Task[Any]] = set()
        self._closed = False

    @property
    def pending(self) -> int:
        return len(self._tasks)

    def spawn(self, coro: Coroutine[Any, Any, Any], *, name: str) -> asyncio.Task[Any]:
        if self._closed:
            coro.close()  # avoid "coroutine was never awaited"
            raise RuntimeError("supervisor is shut down")
        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)
        task.add_done_callback(self._finished)
        return task

    def _finished(self, task: asyncio.Task[Any]) -> None:
        self._tasks.discard(task)
        if task.cancelled():
            return
        exc = task.exception()  # marks the exception as retrieved
        if exc is not None:
            self._on_error(task.get_name(), exc)

    async def shutdown(self, grace: float) -> int:
        """Stop accepting work, give tasks `grace` seconds, cancel the rest.

        Returns the number of tasks that had to be cancelled.
        """
        self._closed = True
        pending = set(self._tasks)
        if not pending:
            return 0
        _, still_running = await asyncio.wait(pending, timeout=grace)
        for task in still_running:
            task.cancel()
        if still_running:
            await asyncio.gather(*still_running, return_exceptions=True)
        return len(still_running)
