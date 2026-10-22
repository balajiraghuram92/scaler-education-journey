import dataclasses
from collections.abc import Callable

import pytest

from resilient import Response, RetryingClient, UpstreamError


class ScriptedTransport:
    """Fake upstream: replays responses and records the prompts it received."""

    def __init__(self, *script: Response) -> None:
        self._script = list(script)
        self.prompts: list[str] = []

    async def __call__(self, prompt: str) -> Response:
        self.prompts.append(prompt)
        if not self._script:
            raise AssertionError("transport called more times than the script allows")
        return self._script.pop(0)


class SleepRecorder:
    def __init__(self) -> None:
        self.delays: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


@pytest.fixture
def sleeps() -> SleepRecorder:
    return SleepRecorder()


@pytest.fixture
def make_client(sleeps) -> Callable[..., RetryingClient]:
    def factory(transport: ScriptedTransport, **kw) -> RetryingClient:
        kw.setdefault("max_attempts", 4)
        kw.setdefault("base_delay", 1.0)
        return RetryingClient(transport, sleeps, **kw)

    return factory


@pytest.mark.asyncio
async def test_success_first_try_does_not_sleep(make_client, sleeps):
    transport = ScriptedTransport(Response(200, "hello"))
    assert await make_client(transport).call("p") == "hello"
    assert sleeps.delays == [], "no sleep on first-try success"
    assert transport.prompts == ["p"]


@pytest.mark.asyncio
async def test_exponential_backoff_schedule(make_client, sleeps):
    transport = ScriptedTransport(Response(503), Response(503), Response(500), Response(200, "ok"))
    assert await make_client(transport).call("p") == "ok"
    assert sleeps.delays == [1.0, 2.0, 4.0]
    assert transport.prompts == ["p"] * 4


@pytest.mark.asyncio
async def test_retry_after_is_honoured_but_capped(make_client, sleeps):
    transport = ScriptedTransport(
        Response(429, retry_after=10.0), Response(429, retry_after=120.0), Response(200, "ok")
    )
    await make_client(transport).call("p")
    assert sleeps.delays == [10.0, 30.0]


@pytest.mark.asyncio
async def test_retry_after_never_shortens_backoff(make_client, sleeps):
    transport = ScriptedTransport(
        Response(503), Response(503, retry_after=0.1), Response(503, retry_after=1.0), Response(200, "ok")
    )
    await make_client(transport).call("p")
    assert sleeps.delays == [1.0, 2.0, 4.0], "use max(backoff, retry_after)"


@pytest.mark.asyncio
async def test_backoff_is_capped_at_max_delay(make_client, sleeps):
    transport = ScriptedTransport(*[Response(502)] * 5, Response(200, "ok"))
    client = make_client(transport, max_attempts=6, max_delay=5.0)
    await client.call("p")
    assert sleeps.delays == [1.0, 2.0, 4.0, 5.0, 5.0]


@pytest.mark.asyncio
async def test_gives_up_after_max_attempts(make_client, sleeps):
    transport = ScriptedTransport(*[Response(503)] * 4)
    with pytest.raises(UpstreamError, match="4 attempts") as excinfo:
        await make_client(transport).call("p")
    assert excinfo.value.last_status == 503
    assert excinfo.value.attempts == 4
    assert len(sleeps.delays) == 3, "must not sleep after the final attempt"


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [400, 401, 404])
async def test_non_retryable_status_fails_fast(make_client, sleeps, status):
    transport = ScriptedTransport(Response(status))
    with pytest.raises(UpstreamError) as excinfo:
        await make_client(transport).call("p")
    assert excinfo.value.attempts == 1
    assert excinfo.value.last_status == status
    assert sleeps.delays == []
    assert len(transport.prompts) == 1


def test_max_attempts_must_be_positive(sleeps):
    with pytest.raises(ValueError):
        RetryingClient(ScriptedTransport(), sleeps, max_attempts=0)


@pytest.mark.asyncio
async def test_single_attempt_client_never_sleeps(make_client, sleeps):
    transport = ScriptedTransport(Response(503))
    with pytest.raises(UpstreamError, match="1 attempts"):
        await make_client(transport, max_attempts=1).call("p")
    assert sleeps.delays == []


def test_response_is_frozen_with_defaults():
    r = Response(200)
    assert r.body == "" and r.retry_after is None
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.status = 500
