# Mocking, Test Doubles and Async Tests

Most flaky and misleading tests in backend and AI code trace back to the same mistake: replacing the wrong thing, in the wrong place, with a double that agrees with whatever the test says. Senior interviewers probe three things here: whether you know where `patch` actually takes effect, whether you prefer fakes to interaction-asserting mocks, and whether you can test `async` code and HTTP clients without a network.

## Concepts Covered

### The test-double vocabulary and why fakes usually win

A **dummy** fills a parameter, a **stub** returns canned answers, a **spy** records calls, a **mock** has expectations about calls, and a **fake** is a working lightweight implementation (an in-memory repository, a scripted LLM client). Mocks couple your test to the implementation: they assert *how* the code talked to a collaborator, so a harmless refactor (batching two calls into one) breaks tests that never found a bug. Fakes let you assert *outcomes*. Use a mock when the interaction itself is the contract, for example "the payment provider was called exactly once with this idempotency key". Use a fake for everything that has state or behaviour worth modelling.

### `Mock`, `MagicMock`, `spec` and `autospec`

`Mock` creates attributes on demand and records every call. `MagicMock` is a `Mock` that also configures the magic methods (`__len__`, `__iter__`, `__enter__`, `__bool__` and so on), which is why `len(MagicMock())` is `0` while `len(Mock())` raises `TypeError`. Unrestricted mocks hide typos: `mock.sned(...)` simply works. Restrict them:

- `Mock(spec=Gateway)` only allows attributes that exist on `Gateway`, so a typo raises `AttributeError`. It does **not** check call signatures of its methods.
- `create_autospec(Gateway, instance=True)` (or `patch(..., autospec=True)`) also copies signatures, so calling `send` with the wrong arguments raises `TypeError`.
- `spec_set` additionally forbids setting attributes that do not exist.

`side_effect` controls behaviour per call: an exception instance or class is raised, an iterable yields one item per call (an exception inside the iterable is raised, and an exhausted iterable raises `StopIteration`), and a function is called with the same arguments and its return value is used.

```python
from unittest.mock import Mock, create_autospec


class Gateway:
    def send(self, to: str, body: str) -> bool: ...


loose = Mock(spec=Gateway)
loose.send("a")                      # accepted: spec checks names, not signatures

strict = create_autospec(Gateway, instance=True)
try:
    strict.send("a")
except TypeError as exc:
    print(exc)

flaky = Mock(side_effect=[1, ValueError("boom"), 3])
print(flaky())
```

```text
missing a required argument: 'body'
1
```

Since Python 3.5 a mock raises `AttributeError` for misspelled assertion helpers such as `assert_called_once_wiht`, instead of silently passing; this guard is lost if you construct the mock with a permissive `unsafe=True`.

### Patch where the name is looked up

`patch("a.b")` replaces the attribute `b` on module `a` for the duration of the test. Code that did `from gateway import send_email` holds its **own** reference in its module namespace, so patching `gateway.send_email` does not affect it. Patch the name where it is *used* (`billing.send_email`). Code that calls `gateway.send_email(...)` through the module looks the attribute up at call time, so there the opposite target is right.

```python
import sys
import types
from unittest.mock import patch

gateway = types.ModuleType("gateway")
exec("def send_email(to, body):\n    return 'REAL'\n", gateway.__dict__)
sys.modules["gateway"] = gateway

billing = types.ModuleType("billing")
exec(
    "from gateway import send_email\n"
    "import gateway\n"
    "def notify_from(): return send_email('a', 'b')\n"
    "def notify_attr(): return gateway.send_email('a', 'b')\n",
    billing.__dict__,
)
sys.modules["billing"] = billing

with patch("gateway.send_email", return_value="FAKE"):
    print(billing.notify_from(), billing.notify_attr())
with patch("billing.send_email", return_value="FAKE"):
    print(billing.notify_from(), billing.notify_attr())
```

```text
REAL FAKE
FAKE REAL
```

Other tools: `patch.object(obj, "name")` avoids string targets, `patch.dict` temporarily edits a mapping such as `os.environ`, and stacked `@patch` decorators inject arguments bottom-up. Always prefer `autospec=True` so the replacement matches the real signature. In pytest, `monkeypatch.setattr` follows the same lookup rule and is usually the simpler tool; the real fix for hard-to-patch code is **dependency injection**: pass the client or the clock in.

### A fake plus injected clock beats a stack of patches

The service below takes an LLM client and a clock as constructor arguments. The fake LLM replays a script (strings are replies, exceptions are raised) and records prompts; the fake clock is advanced by hand. I ran this scenario: the first call times out and is retried, the second call within the TTL is served from cache, and after six minutes the model is called again.

```python
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Protocol


class LLMClient(Protocol):
    async def complete(self, prompt: str, *, max_tokens: int) -> str: ...


@dataclass
class FakeLLM:
    script: list[str | Exception]
    prompts: list[str] = field(default_factory=list)

    async def complete(self, prompt: str, *, max_tokens: int) -> str:
        self.prompts.append(prompt)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class Summarizer:
    def __init__(self, llm: LLMClient, clock: Callable[[], datetime],
                 ttl: timedelta = timedelta(minutes=5)) -> None:
        self._llm, self._clock, self._ttl = llm, clock, ttl
        self._cache: dict[str, tuple[datetime, str]] = {}

    async def summarize(self, doc: str) -> str:
        now = self._clock()
        hit = self._cache.get(doc)
        if hit and now - hit[0] < self._ttl:
            return hit[1]
        for attempt in range(2):
            try:
                text = await self._llm.complete(f"Summarize: {doc}", max_tokens=128)
                break
            except TimeoutError:
                if attempt == 1:
                    raise
        self._cache[doc] = (now, text)
        return text
```

The test, with `llm = FakeLLM([TimeoutError("slow"), "short", "fresh"])`, asserts `await s.summarize("doc") == "short"` and `len(llm.prompts) == 2` (timeout plus retry), then the same call returns the cached value with the count still `2`, then after `clock.advance(minutes=6)` it returns `"fresh"` and the count is `3`. No patching, no real sleeping, no flakiness.

### `AsyncMock` and running async tests

Calling an `AsyncMock` returns a coroutine; awaiting it yields `return_value` or applies `side_effect`. It adds `assert_awaited_once_with`, `await_count` and `await_args`. `patch` on an `async def` target automatically creates an `AsyncMock`. A `MagicMock` standing in for an async method is a classic bug: calling it returns a plain value, and `await` on that raises `TypeError`.

```python
import asyncio
from unittest.mock import AsyncMock


async def main() -> None:
    llm = AsyncMock()
    llm.complete.return_value = "hi"
    coro = llm.complete("p", temperature=0)
    print(type(coro).__name__, await coro)
    llm.complete.assert_awaited_once_with("p", temperature=0)

    llm.complete.side_effect = [TimeoutError("slow"), "ok"]
    try:
        await llm.complete("p")
    except TimeoutError as exc:
        print("timeout:", exc)
    print(await llm.complete("p"))


asyncio.run(main())
```

```text
coroutine hi
timeout: slow
ok
```

pytest does not run coroutines on its own. Two common plugins fix that. **pytest-asyncio** in its default `strict` mode needs `@pytest.mark.asyncio` on tests and `@pytest_asyncio.fixture` on async fixtures; setting `asyncio_mode = "auto"` removes the markers. **anyio** ships its own plugin: mark tests with `@pytest.mark.anyio` and provide the `anyio_backend` fixture, which also lets you run the same test on trio. Pick one per repo, and keep event-loop scope aligned with your fixtures' scope or you will see "attached to a different loop" errors.

### Testing HTTP clients: `httpx.MockTransport` and respx

Inject the `httpx.AsyncClient` rather than creating it inside the function. A `MockTransport` takes a handler `Request -> Response` (sync or async) and replaces the network, while everything above it (base URL, headers, JSON encoding, retries, timeouts) is real code under test.

```python
import json

import httpx
import pytest


async def get_embedding(client: httpx.AsyncClient, text: str) -> list[float]:
    resp = await client.post("/v1/embeddings", json={"input": text})
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


@pytest.mark.asyncio
async def test_embedding_request_shape_and_parse() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": [{"embedding": [0.1, 0.2]}]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://llm.test") as c:
        assert await get_embedding(c, "hello") == [0.1, 0.2]

    assert seen[0].url.path == "/v1/embeddings"
    assert json.loads(seen[0].content) == {"input": "hello"}
```

The `respx` library offers route-based mocking (`respx.get(url).mock(return_value=httpx.Response(...))`, with `side_effect` for errors and sequences) and asserts which routes were called; it is handy when you cannot inject the client. Always add a test for the failure paths that production hits: 429 with `Retry-After`, 500, a read timeout (`httpx.ReadTimeout`) and malformed JSON.

### Freezing time

Time is the other hidden global. Best option: inject a clock callable as above. Second best: a library such as `freezegun` (`freeze_time`) or `time-machine` (`travel`), which patch the time functions for you; both are fast but can surprise code that cached a reference to `time.monotonic` or uses the event loop's own clock. Avoid `patch("time.sleep")` unless you patch the name in the module that uses it, and prefer injecting a `sleep` callable in retry code.

## Practical Backend Scenario

Your LLM gateway wraps a vendor API with retries, a response cache and cost accounting. A production incident shows duplicate vendor calls after a timeout. The reproduction needs three things at once: a scripted failure (first call times out), the passage of time (cache TTL), and an assertion on the exact request count. With a scripted fake client, an injected clock and an httpx `MockTransport` for the wire format, you reproduce it in a 20-line async test with no sleeps, then fix the bug and keep the test as a regression guard.

## Practice Loop

1. Write `Summarizer` and `FakeLLM` from this lesson, then write the three-step async test using `pytest.mark.asyncio` (or `anyio`) and a `FakeClock`.
2. Replace `FakeLLM` with `AsyncMock(spec=LLMClient)`; note which assertions you now have to write by hand and which refactors break the test.
3. Re-create the `billing`/`gateway` module pair, and predict, then verify, the output of patching each target for both import styles.
4. Use `create_autospec` on a class with a method that takes two arguments and watch the wrong call fail with `TypeError`.
5. Write a `MockTransport` handler that returns 429 twice then 200, and test that your retry layer sleeps (through an injected `sleep`) the expected total delay.
6. Make a deliberate bug: use `MagicMock` for an async method, and read the error.

## Evidence of Understanding

- I can explain why `patch("gateway.send_email")` fails to affect `from gateway import send_email` code, and choose the right target.
- I can state what `spec`, `spec_set` and `autospec` each guarantee, and which one catches a wrong argument count.
- I can justify replacing a mock-based test with a fake, and name a case where a mock is still the right tool.
- I can write an async test with `AsyncMock`, assert awaits, and explain why `MagicMock` fails for async methods.
- I can test an httpx-based client including failure paths without any real network.

## Interview Questions to Rehearse

### Q: `patch` did not work. What do you check first?

The target. `patch` replaces an attribute on the module you name, so for `from x import y` code I must patch `consumer.y`, not `x.y`. Then I check that the patch is active at call time (not applied after the object under test captured the reference), and whether `autospec` is hiding a signature problem.

### Q: Mock versus MagicMock versus autospec?

`Mock` makes any attribute; `MagicMock` also supports magic methods. Both accept typos and wrong arities unless restricted. `spec` limits attribute names, `spec_set` also limits setting, and `autospec` additionally enforces signatures. I use autospec by default so tests fail when the real interface changes.

### Q: Why prefer fakes over mocks?

Fakes keep tests about behaviour, and they survive refactors. A fake repository also doubles as the in-memory implementation for local development. Mocks encode call sequences, so they break on refactors and can pass while the real integration is wrong. I run the same contract tests against the fake and the real adapter to keep them honest.

### Q: How do you test async code?

Use a plugin (pytest-asyncio or anyio) to run coroutines, `AsyncMock` or an async fake for collaborators, and inject the HTTP client with `httpx.MockTransport` so serialization and error handling are real. I cover cancellation and timeouts, not only the happy path.

### Q: How do you handle time in tests?

Inject a clock and a `sleep` function so tests advance time explicitly. If I cannot change the code, I use `freezegun` or `time-machine`, knowing they can miss references cached before the freeze and do not control the asyncio loop clock.

### Q: When is a mock the right tool?

When the interaction is the requirement: the payment provider was called exactly once with an idempotency key, the audit logger received the event. Even then I assert on a spy or `assert_called_once_with` on one narrow boundary, never on internal collaborators.

## Common Pitfalls

- Patching the definition site instead of the use site.
- Using `MagicMock` where `AsyncMock` is needed, or forgetting `await` on an `AsyncMock`, which leaves a never-awaited coroutine warning.
- Unspecced mocks that silently accept misspelled methods and wrong arguments.
- Asserting call counts and orders on internal collaborators, so refactors break tests.
- Mutating shared fixtures with `side_effect` lists across tests; each test needs its own script.
- Real `time.sleep` or real network calls hidden in a retry layer, making the suite slow and flaky.
- Mixing pytest-asyncio and anyio markers in one repo, or mismatched loop scopes.

## Suggested Extension

Build a `FakeVendorServer` as an `httpx.MockTransport` handler that implements a tiny stateful LLM API (rate limit counter, idempotency-key cache, 429 with `Retry-After`). Use it to test your retry and circuit-breaker layers end to end, and run the same suite against a real staging key marked as an integration test.
