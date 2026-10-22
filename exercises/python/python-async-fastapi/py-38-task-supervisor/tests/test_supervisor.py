import asyncio
import gc
import inspect

import pytest

from supervisor import TaskSupervisor


@pytest.mark.asyncio
async def test_error_is_reported_not_lost():
    seen: list[tuple[str, str]] = []
    sup = TaskSupervisor(lambda n, e: seen.append((n, str(e))))

    async def boom() -> None:
        raise ValueError("lost?")

    sup.spawn(boom(), name="audit")
    await sup.shutdown(grace=1)
    assert seen == [("audit", "lost?")], "on_error must receive the task name and the exception"


@pytest.mark.asyncio
async def test_on_error_called_exactly_once_per_failure():
    seen: list[str] = []
    sup = TaskSupervisor(lambda n, e: seen.append(n))

    async def boom() -> None:
        raise RuntimeError("x")

    task = sup.spawn(boom(), name="once")
    await asyncio.wait([task])
    await sup.shutdown(grace=0.05)
    await sup.shutdown(grace=0.05)
    assert seen == ["once"], "on_error must be called exactly once per failed task"


@pytest.mark.asyncio
async def test_spawn_returns_named_task_and_pending_tracks_it():
    sup = TaskSupervisor(lambda n, e: None)
    gate = asyncio.Event()

    async def wait() -> None:
        await gate.wait()

    task = sup.spawn(wait(), name="waiter")
    assert isinstance(task, asyncio.Task) and task.get_name() == "waiter"
    assert sup.pending == 1, "an unfinished task must count as pending"
    gate.set()
    await task
    await asyncio.sleep(0)  # let the done callback run
    assert sup.pending == 0, "a finished task must be removed from the supervisor"


@pytest.mark.asyncio
async def test_supervisor_keeps_a_strong_reference():
    done: list[str] = []
    sup = TaskSupervisor(lambda n, e: None)

    async def work() -> None:
        await asyncio.sleep(0.02)
        done.append("ran")

    sup.spawn(work(), name="forgotten")  # the caller drops the returned task
    gc.collect()
    await sup.shutdown(grace=1)
    assert done == ["ran"], "a task nobody else references must not be garbage collected"


@pytest.mark.asyncio
async def test_shutdown_waits_for_fast_and_cancels_slow():
    log: list[str] = []
    sup = TaskSupervisor(lambda n, e: log.append(f"error:{n}"))

    async def fast() -> None:
        await asyncio.sleep(0.01)
        log.append("fast done")

    async def slow() -> None:
        try:
            await asyncio.sleep(5)
        finally:
            log.append("slow cleaned")

    sup.spawn(fast(), name="fast")
    sup.spawn(slow(), name="slow")
    cancelled = await sup.shutdown(grace=0.1)
    assert cancelled == 1, "only the slow task had to be cancelled"
    assert sup.pending == 0
    assert log == ["fast done", "slow cleaned"], "cancellation must complete cleanup and must not be an error"


@pytest.mark.asyncio
async def test_spawn_after_shutdown_is_rejected_and_closes_coroutine():
    sup = TaskSupervisor(lambda n, e: None)
    await sup.shutdown(grace=0)

    async def noop() -> None: ...

    coro = noop()
    with pytest.raises(RuntimeError):
        sup.spawn(coro, name="late")
    assert inspect.getcoroutinestate(coro) == inspect.CORO_CLOSED, "the rejected coroutine must be closed"


@pytest.mark.asyncio
async def test_shutdown_is_idempotent():
    sup = TaskSupervisor(lambda n, e: None)

    async def slow() -> None:
        await asyncio.sleep(5)

    sup.spawn(slow(), name="s")
    first = await sup.shutdown(grace=0.01)
    second = await sup.shutdown(grace=0.01)
    assert (first, second) == (1, 0), "second shutdown has nothing left to cancel"


@pytest.mark.asyncio
async def test_shutdown_with_no_tasks_returns_zero():
    sup = TaskSupervisor(lambda n, e: None)
    assert await sup.shutdown(grace=0.01) == 0
