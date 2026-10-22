import inspect
from typing import assert_type

import pytest

from retry import aretry, retry


def test_retries_then_succeeds_with_backoff_schedule():
    delays: list[float] = []
    calls = 0

    @retry(attempts=4, base_delay=1.0, sleep=delays.append)
    def fetch(url: str, *, timeout: float = 1.0) -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ConnectionError("down")
        return f"ok:{url}:{timeout}"

    result = fetch("u", timeout=2.0)
    assert_type(result, str)
    assert result == "ok:u:2.0", "arguments must be forwarded and the result returned"
    assert calls == 3
    assert delays == [1.0, 2.0]


def test_gives_up_and_reraises_last_error_without_final_sleep():
    delays: list[float] = []
    calls = 0

    @retry(attempts=3, base_delay=1.0, sleep=delays.append)
    def always_fails() -> None:
        nonlocal calls
        calls += 1
        raise ConnectionError(f"down {calls}")

    with pytest.raises(ConnectionError, match="down 3"):
        always_fails()
    assert calls == 3
    assert delays == [1.0, 2.0], "no sleep after the final attempt"


def test_other_exceptions_are_not_retried():
    calls = 0

    @retry(attempts=5)
    def bad_input(x: int) -> int:
        nonlocal calls
        calls += 1
        raise ValueError("bad")

    with pytest.raises(ValueError):
        bad_input(1)
    assert calls == 1


def test_on_accepts_a_tuple_of_exceptions():
    calls = 0

    @retry(attempts=3, on=(TimeoutError, ConnectionError))
    def flaky() -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TimeoutError
        if calls == 2:
            raise ConnectionError
        return "done"

    assert flaky() == "done"
    assert calls == 3


def test_signature_and_metadata_are_preserved():
    @retry(attempts=2)
    def complete(prompt: str, *, max_tokens: int = 256) -> str:
        """Call the model."""
        return prompt

    assert complete.__name__ == "complete"
    assert complete.__doc__ == "Call the model."
    assert str(inspect.signature(complete)) == "(prompt: str, *, max_tokens: int = 256) -> str"
    assert hasattr(complete, "__wrapped__"), "use functools.wraps"


def test_invalid_attempts_rejected_when_factory_is_called():
    with pytest.raises(ValueError, match="attempts must be >= 1"):
        retry(attempts=0)
    with pytest.raises(ValueError, match="attempts must be >= 1"):
        aretry(attempts=-1)


def test_default_sleep_is_a_noop():
    calls = 0

    @retry(attempts=3, base_delay=100.0)
    def flaky() -> int:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ConnectionError
        return calls

    assert flaky() == 3, "the default sync sleep must not really wait"


@pytest.mark.asyncio
async def test_async_retry_uses_injected_sleep():
    delays: list[float] = []
    calls = 0

    async def record(seconds: float) -> None:
        delays.append(seconds)

    @aretry(attempts=3, base_delay=0.5, sleep=record)
    async def embed(text: str) -> list[float]:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ConnectionError("blip")
        return [float(len(text))]

    assert await embed("abcd") == [4.0]
    assert delays == [0.5, 1.0]
    assert inspect.iscoroutinefunction(embed), "the async wrapper must itself be a coroutine function"


@pytest.mark.asyncio
async def test_async_gives_up_and_skips_unmatched_errors():
    delays: list[float] = []

    async def record(seconds: float) -> None:
        delays.append(seconds)

    @aretry(attempts=2, sleep=record, base_delay=1.0)
    async def down() -> None:
        raise ConnectionError("still down")

    with pytest.raises(ConnectionError, match="still down"):
        await down()
    assert delays == [1.0]

    calls = 0

    @aretry(attempts=4, sleep=record)
    async def invalid() -> None:
        nonlocal calls
        calls += 1
        raise KeyError("x")

    with pytest.raises(KeyError):
        await invalid()
    assert calls == 1
