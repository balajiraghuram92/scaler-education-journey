import asyncio

import pytest

from lifecycle import Lifecycle, Readiness, ShuttingDown, run_checks


async def ok():
    return None


async def provider_down():
    raise RuntimeError("503")


@pytest.mark.asyncio
async def test_track_counts_and_releases_on_error():
    lc = Lifecycle()
    assert lc.inflight == 0 and lc.draining is False
    async with lc.track():
        assert lc.inflight == 1
        async with lc.track():
            assert lc.inflight == 2, "nested tracking counts each unit of work"
    assert lc.inflight == 0
    with pytest.raises(ValueError):
        async with lc.track():
            raise ValueError("boom")
    assert lc.inflight == 0, "the count must drop even when the body raises"


@pytest.mark.asyncio
async def test_shutdown_waits_for_inflight_and_rejects_new_work():
    lc = Lifecycle()
    started = asyncio.Event()
    release = asyncio.Event()

    async def work():
        async with lc.track():
            started.set()
            await release.wait()

    task = asyncio.create_task(work())
    await started.wait()
    shutdown = asyncio.create_task(lc.shutdown(2.0))
    await asyncio.sleep(0.02)
    assert not shutdown.done(), "shutdown must wait while work is still in flight"
    assert lc.draining is True
    with pytest.raises(ShuttingDown):
        async with lc.track():
            pass
    assert lc.inflight == 1, "a rejected track() must not change the count"
    release.set()
    assert await shutdown is True
    assert task.done() and lc.inflight == 0


@pytest.mark.asyncio
async def test_shutdown_times_out_without_cancelling_work():
    lc = Lifecycle()
    started, release = asyncio.Event(), asyncio.Event()
    finished = []

    async def work():
        async with lc.track():
            started.set()
            await release.wait()
            finished.append(True)

    task = asyncio.create_task(work())
    await started.wait()
    assert await lc.shutdown(0.05) is False, "timeout while work is still running returns False"
    assert not task.cancelled() and not task.done(), "shutdown must not cancel the in-flight work"
    release.set()
    await task
    assert finished == [True] and lc.inflight == 0


@pytest.mark.asyncio
async def test_shutdown_with_nothing_in_flight_returns_true_immediately():
    lc = Lifecycle()
    assert await lc.shutdown(0.0) is True
    assert lc.draining is True
    assert await lc.shutdown(0.0) is True, "shutdown can be called again"


@pytest.mark.asyncio
async def test_checks_run_concurrently_and_report_ok():
    a_started, b_started = asyncio.Event(), asyncio.Event()

    async def check_a():
        a_started.set()
        await b_started.wait()  # only completes if check_b is running at the same time

    async def check_b():
        b_started.set()
        await a_started.wait()

    result = await run_checks(Lifecycle(), {"a": check_a, "b": check_b}, timeout=1.0)
    assert result == Readiness(True, {"a": "ok", "b": "ok"}), "checks must run concurrently and be reported by name"


@pytest.mark.asyncio
async def test_timeout_and_error_strings_never_raise():
    async def hangs():
        await asyncio.sleep(5)

    async def broken():
        raise ConnectionError("down")

    result = await run_checks(Lifecycle(), {"db": hangs, "cache": broken, "fine": ok}, timeout=0.05)
    assert result.checks == {"db": "timeout", "cache": "error: ConnectionError", "fine": "ok"}
    assert result.ready is False, "all checks are hard by default"


@pytest.mark.asyncio
async def test_soft_dependency_does_not_flip_readiness():
    lc = Lifecycle()
    r = await run_checks(lc, {"postgres": ok, "llm_provider": provider_down}, hard={"postgres"})
    assert r.ready and r.checks["llm_provider"] == "error: RuntimeError", "soft failures are reported, not fatal"
    r2 = await run_checks(lc, {"postgres": provider_down, "llm_provider": ok}, hard={"postgres"})
    assert not r2.ready, "a failing hard dependency flips readiness"


@pytest.mark.asyncio
async def test_hard_edge_cases():
    lc = Lifecycle()
    assert await run_checks(lc, {}) == Readiness(True, {}), "no checks means ready"
    r = await run_checks(lc, {"x": provider_down}, hard=set())
    assert r.ready is True and r.checks == {"x": "error: RuntimeError"}, "an empty hard set never blocks readiness"


@pytest.mark.asyncio
async def test_draining_short_circuits_checks():
    called = []

    async def check():
        called.append(1)

    lc = Lifecycle()
    await lc.shutdown(0.01)
    r = await run_checks(lc, {"db": check})
    assert r == Readiness(False, {"lifecycle": "draining"}), "a draining service reports not ready immediately"
    assert called == [], "no check may run while draining"
