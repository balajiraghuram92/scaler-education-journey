import asyncio
import inspect

import pytest

from resilience import retry


def run(coro):
    return asyncio.run(coro)


def test_sync_retries_then_succeeds_with_exponential_backoff():
    calls, naps = [], []

    @retry(attempts=3, backoff_s=0.5, sleep=naps.append)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("down")
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3, f"expected 3 calls, got {len(calls)}"
    assert naps == [0.5, 1.0], f"expected backoff sleeps [0.5, 1.0], got {naps}"


def test_sync_gives_up_and_reraises_the_last_exception_unchanged():
    errors, naps = [], []

    @retry(attempts=3, backoff_s=1.0, sleep=naps.append)
    def always():
        err = TimeoutError(f"try {len(errors) + 1}")
        errors.append(err)
        raise err

    with pytest.raises(TimeoutError) as info:
        always()
    assert len(errors) == 3, "must make exactly `attempts` calls"
    assert info.value is errors[-1], "re-raise the last exception object, not a new one"
    assert naps == [1.0, 2.0], f"no sleep after the final attempt; got {naps}"


def test_async_function_is_really_retried_and_stays_a_coroutine_function():
    calls, naps = [], []

    async def asleep(seconds):
        naps.append(seconds)

    @retry(attempts=3, backoff_s=0.25, asleep=asleep)
    async def fetch(x):
        calls.append(x)
        if len(calls) < 3:
            raise ConnectionError("flaky")
        return x * 2

    assert inspect.iscoroutinefunction(fetch), "the wrapper of an async function must itself be async def"
    assert run(fetch(21)) == 42
    assert calls == [21, 21, 21], "the coroutine must be awaited inside the try so failures are retried"
    assert naps == [0.25, 0.5], f"async backoff must use the injected asleep, got {naps}"


def test_async_gives_up_and_reraises_the_last_exception():
    errors = []

    async def asleep(seconds):
        pass

    @retry(attempts=2, asleep=asleep)
    async def always():
        err = ConnectionError(f"n{len(errors)}")
        errors.append(err)
        raise err

    with pytest.raises(ConnectionError) as info:
        run(always())
    assert len(errors) == 2 and info.value is errors[-1]


def test_metadata_is_preserved_for_sync_and_async():
    @retry()
    def embed(text: str) -> list[float]:
        """Embed text."""
        return [1.0]

    @retry()
    async def aembed(text: str) -> list[float]:
        """Embed async."""
        return [1.0]

    assert embed.__name__ == "embed" and embed.__doc__ == "Embed text."
    assert aembed.__name__ == "aembed" and aembed.__doc__ == "Embed async."
    assert not inspect.iscoroutinefunction(embed), "a sync function must stay sync"


def test_unlisted_exceptions_propagate_immediately_without_sleeping():
    calls, naps = [], []

    @retry(attempts=5, backoff_s=1.0, sleep=naps.append)
    def bug():
        calls.append(1)
        raise KeyError("bug")

    with pytest.raises(KeyError):
        bug()
    assert len(calls) == 1 and naps == [], "an exception not listed in `on` must not be retried"

    acalls = []

    @retry(attempts=5, asleep=lambda s: asyncio.sleep(0))
    async def abug():
        acalls.append(1)
        raise ValueError("bug")

    with pytest.raises(ValueError):
        run(abug())
    assert len(acalls) == 1, "async functions must not retry unlisted exceptions either"


def test_custom_on_arguments_and_return_values_pass_through():
    calls = []

    @retry(attempts=3, on=(ValueError,), sleep=lambda s: None)
    def parse(a, b=0):
        calls.append((a, b))
        if len(calls) == 1:
            raise ValueError("bad")
        return a + b

    assert parse(1, b=2) == 3
    assert calls == [(1, 2), (1, 2)], "arguments must be forwarded on every attempt"

    @retry(attempts=3, on=(ValueError,), sleep=lambda s: None)
    def connection_error():
        raise ConnectionError("not listed any more")

    with pytest.raises(ConnectionError):
        connection_error()


def test_invalid_attempts_rejected_when_the_factory_is_called():
    for bad in (0, -3):
        with pytest.raises(ValueError):
            retry(attempts=bad)
    calls = []

    @retry(attempts=1)
    def once():
        calls.append(1)
        raise ConnectionError

    with pytest.raises(ConnectionError):
        once()
    assert len(calls) == 1, "attempts=1 means a single call and no retry"
