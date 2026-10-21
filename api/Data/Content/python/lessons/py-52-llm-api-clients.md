# Building Robust LLM API Clients

An LLM call is the slowest, flakiest and most expensive HTTP request in your system: seconds of latency, rate limits that fire under load, 5xx during provider incidents, and a bill that grows with every retry. A client that is "just `httpx.post`" works in the demo and melts in production, either by hammering a throttled provider or by silently double-billing. In AI and FDE interviews, how you talk about timeouts, retries, streaming and cost tells the interviewer whether you have run one of these services at load.

## Concepts Covered

### The shape of a chat-completions API

Most providers expose something close to one generic contract: `POST /v1/chat/completions` with a model name, a list of role-tagged messages and a token cap; the response carries `choices`, a `finish_reason`, and a `usage` block with prompt and completion token counts. We will build against that shape with `httpx` so nothing here depends on a vendor. The first design rule is to **own your types**: parse the provider JSON once, at the edge, into your own Pydantic models, and let the rest of the codebase see only those.

```python
from __future__ import annotations

import asyncio
import json
import math
import random
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Literal

import httpx
from pydantic import BaseModel, Field, ValidationError


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    max_tokens: int = Field(512, gt=0)
    temperature: float = Field(0.0, ge=0.0, le=2.0)


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int


class ChatResponse(BaseModel):
    id: str
    model: str
    text: str
    finish_reason: str
    usage: Usage


class LLMError(Exception):
    def __init__(self, message: str, *, status: int | None = None,
                 retry_after: float | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after
```

Notice `max_tokens` is required to be positive and defaulted. An unbounded completion is a cost and latency bug waiting to happen, so the client makes the cap a first-class, validated field.

### Timeouts: connect, read, write, pool

`httpx` defaults to five seconds for every phase, and `httpx.Timeout(None)` disables them, which is how requests hang forever. The four phases mean different things. **Connect** is the TCP and TLS handshake: keep it short (2 to 5 seconds), because a slow connect means a bad network path and a retry will probably land elsewhere. **Read** is the longest wait for *the next chunk of bytes*, not the total duration. For a non-streaming call the first byte only arrives when the whole completion is done, so read must cover the slowest legitimate generation (30 to 60 seconds). For a streaming call the read timeout is a stall detector between tokens, so it can be much tighter in spirit, yet a three-minute stream that emits a token every second never trips it. **Write** covers sending the body, and **pool** is how long you wait for a free connection from the pool, a symptom that you are out of `max_connections`.

Because the per-phase timeouts never bound the *total* time, you also need a deadline around the whole operation. Python 3.11+ gives you `asyncio.timeout()`, and it cancels the in-flight request cleanly, as the first test below shows.

### Retries: what, when, how long

The retry rules that survive a production incident are short.

1. **Retry only transient failures:** 429, 500, 502, 503, 504, plus connect errors and read timeouts. Never retry 400, 401, 403, 404 or 422. A `context_length_exceeded` 400 will fail identically forever and each attempt is billed for validation work or wastes a rate-limit slot.
2. **Exponential backoff with full jitter:** sleep `uniform(0, min(cap, base * 2**attempt))`. Without jitter, every client throttled at the same moment retries at the same moment, a thundering herd that re-triggers the 429.
3. **Honour `Retry-After`:** it is either delta-seconds or an HTTP-date. Take the *larger* of your backoff and the server's hint, and if the hint exceeds your patience (say 30 seconds), fail fast so a queue or the caller can decide.
4. **Bound everything:** a maximum attempt count and a total deadline, otherwise retries multiply tail latency.
5. **Make retried POSTs safe:** a read timeout means the server may have finished the work. Send the same `Idempotency-Key` header on every attempt of one logical call so a provider or gateway that supports it can deduplicate and not bill twice. If your provider does not support idempotency keys, restrict retries to failures where the request definitely did not complete (connect errors and 429/5xx responses).

```python
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    """Retry-After is either delta-seconds or an HTTP-date."""
    if value is None:
        return None
    try:
        seconds = float(value)
        return max(0.0, seconds) if math.isfinite(seconds) else None
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    now = now or datetime.now(timezone.utc)
    return max(0.0, (when - now).total_seconds())


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 4
    base_delay: float = 0.5
    max_delay: float = 20.0
    max_retry_after: float = 30.0

    def delay(self, attempt: int, retry_after: float | None, rng: random.Random) -> float:
        # "Full jitter": uniform(0, min(cap, base * 2**attempt)).
        jittered = rng.uniform(0.0, min(self.max_delay, self.base_delay * 2**attempt))
        return jittered if retry_after is None else max(jittered, retry_after)
```

The clock and the randomness are injectable on purpose (`rng`, plus a `sleep` callable in the client). That is what makes retry logic testable in microseconds instead of real seconds.

### The async client

One `AsyncClient` per process, created at startup and closed at shutdown, because it owns the connection pool and TLS sessions. Creating a client per request throws away keep-alive and pays a handshake every call.

```python
Sleep = Callable[[float], Awaitable[None]]
TRANSPORT_ERRORS = (httpx.ConnectError, httpx.ConnectTimeout,
                    httpx.ReadTimeout, httpx.RemoteProtocolError)


class HttpChatClient:
    def __init__(self, base_url: str, api_key: str, *,
                 transport: httpx.AsyncBaseTransport | None = None,
                 policy: RetryPolicy = RetryPolicy(),
                 sleep: Sleep = asyncio.sleep,
                 rng: random.Random | None = None) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=3.0, read=45.0, write=10.0, pool=5.0),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
            transport=transport,
        )
        self._policy = policy
        self._sleep = sleep
        self._rng = rng or random.Random()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> HttpChatClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def chat(self, req: ChatRequest, *, idempotency_key: str | None = None) -> ChatResponse:
        headers = {"Idempotency-Key": idempotency_key or str(uuid.uuid4())}
        payload = req.model_dump()
        for attempt in range(self._policy.max_attempts):
            retry_after: float | None = None
            try:
                resp = await self._http.post("/v1/chat/completions", json=payload, headers=headers)
            except TRANSPORT_ERRORS as exc:
                error = LLMError(f"transport failure: {type(exc).__name__}")
                error.__cause__ = exc
            else:
                if resp.is_success:
                    return _parse_response(resp.json())
                retry_after = parse_retry_after(resp.headers.get("retry-after"))
                error = LLMError(f"HTTP {resp.status_code}", status=resp.status_code,
                                 retry_after=retry_after)
                if resp.status_code not in RETRYABLE_STATUS:
                    raise error                      # 400/401/403/404/422: retrying cannot help
            exhausted = attempt + 1 >= self._policy.max_attempts
            if exhausted or (retry_after or 0.0) > self._policy.max_retry_after:
                raise error
            await self._sleep(self._policy.delay(attempt, retry_after, self._rng))
        raise AssertionError("unreachable")


def _parse_response(body: dict) -> ChatResponse:
    try:
        choice = body["choices"][0]
        return ChatResponse(id=body["id"], model=body["model"],
                            text=choice["message"]["content"],
                            finish_reason=choice["finish_reason"],
                            usage=Usage(**body["usage"]))
    except (KeyError, IndexError, TypeError, ValidationError) as exc:
        raise LLMError("malformed provider response") from exc
```

Two details deserve a sentence. The idempotency key is generated once, *outside* the loop, so every attempt carries the same value. And the loop catches `httpx` exceptions, not bare `Exception`: since 3.8 `asyncio.CancelledError` derives from `BaseException`, so a plain `except Exception` does not swallow cancellation, but a bare `except:` or `except BaseException` would, and that breaks timeouts and graceful shutdown.

> **Pitfall:** Some providers return 429 for "insufficient quota" or "billing hard limit" as well as for rate limiting. Retrying a quota error is pointless. Inspect the error code in the response body before you treat a 429 as transient.

### Streaming with Server-Sent Events

Streaming turns a 20-second wait into a first token in under a second, and it is how every chat UI works. The wire format is SSE: lines starting with `data:`, events separated by a blank line, `:`-prefixed comment lines as keep-alives, and (for chat-completions style APIs) a final `data: [DONE]` sentinel. Parse it as a small pure function so it can be tested without a network.

```python
async def iter_sse_data(lines: AsyncIterator[str]) -> AsyncIterator[str]:
    """Yield the joined `data:` payload of each complete SSE event."""
    buf: list[str] = []
    async for line in lines:
        if line == "":                      # blank line terminates an event
            if buf:
                yield "\n".join(buf)
                buf.clear()
        elif line.startswith(":"):          # comment / keep-alive
            continue
        elif line.startswith("data:"):
            buf.append(line[5:].removeprefix(" "))
    # A trailing event without its blank line is incomplete: discard it.
```

Add this method to `HttpChatClient`:

```python
    async def stream(self, req: ChatRequest) -> AsyncIterator[str]:
        payload = req.model_dump() | {"stream": True}
        done = False
        async with self._http.stream("POST", "/v1/chat/completions", json=payload) as resp:
            if not resp.is_success:
                await resp.aread()
                raise LLMError(f"HTTP {resp.status_code}", status=resp.status_code,
                               retry_after=parse_retry_after(resp.headers.get("retry-after")))
            async for data in iter_sse_data(resp.aiter_lines()):
                if data == "[DONE]":
                    done = True
                    break
                delta = json.loads(data)["choices"][0]["delta"].get("content")
                if delta:
                    yield delta
        if not done:
            raise LLMError("stream ended without [DONE]; treat the text as truncated")
```

Three production rules hide in there. You may safely retry a stream only **before the first token** has reached the caller; after that, the caller has partial text and a retry would duplicate or contradict it, so surface the error and let the caller decide. A stream that ends without the sentinel is a *truncation* (proxy reset, provider crash) and must not be reported as success. And **cancellation closes the upstream connection**: when the `async with` block unwinds, `httpx` drops the connection, the provider stops generating, and you stop paying for tokens nobody will read. For that to be deterministic, consume the generator with `contextlib.aclosing(...)`, otherwise an abandoned async generator is only finalised later by the event loop.

### Token counting, budgets and cost

The provider's `usage` block is the **billing truth**, but you need an estimate *before* the call to enforce a budget. Count with the model's own tokenizer when you have it (for OpenAI-style models, the `tiktoken` library; other vendors ship token-count endpoints or tokenizers), and fall back to a conservative heuristic such as `len(text) // 4` for admission control only. The robust pattern is **reserve, call, settle**: reserve the worst case (estimated prompt plus the full `max_tokens`), make the call, then replace the reservation with the actual usage. The reservation prevents ten concurrent requests from each believing they fit in the remaining budget.

```python
import logging
import time
from typing import Protocol


class ChatProvider(Protocol):
    async def chat(self, req: ChatRequest) -> ChatResponse: ...


class BudgetExceeded(Exception):
    pass


@dataclass(slots=True)
class TokenBudget:
    limit: int
    used: int = 0
    reserved: int = 0

    def reserve(self, tokens: int) -> None:
        if self.used + self.reserved + tokens > self.limit:
            raise BudgetExceeded(f"need {tokens}, have {self.limit - self.used - self.reserved}")
        self.reserved += tokens

    def settle(self, reserved: int, actual: int) -> None:
        self.reserved -= reserved
        self.used += actual


def estimate_tokens(req: ChatRequest) -> int:
    """Worst case: heuristic prompt size plus the full completion allowance."""
    prompt = sum(len(m.content) for m in req.messages) // 4 + 4 * len(req.messages)
    return prompt + req.max_tokens


# Illustrative USD per 1M tokens: (input, output). Load real prices from config.
PRICES = {"small-model": (0.15, 0.60), "large-model": (3.00, 15.00)}


def cost_usd(model: str, usage: Usage) -> float:
    price_in, price_out = PRICES[model]
    return (usage.prompt_tokens * price_in + usage.completion_tokens * price_out) / 1_000_000
```

`reserve` has no `await` between the check and the update, so on a single event loop it is atomic without a lock. Put an `await` in the middle and two coroutines can both pass the check. Cost belongs in a structured log line per call (model, request id, prompt and completion tokens, dollars, latency) so you can answer "which tenant, which feature, which prompt version burned the money" from logs alone. For ledgers, store integer micro-dollars or `Decimal`, not floats.

### A provider abstraction with `Protocol`

Vendors differ in payload shape, auth and error codes. Hide that behind a `typing.Protocol`: structural typing means a test fake or a second vendor adapter satisfies it without inheriting anything, and wrappers (metering, caching, fallback) compose as decorators around the same interface.

```python
class MeteredProvider:
    """Decorator: budget check before the call, cost log after it."""

    def __init__(self, inner: ChatProvider, budget: TokenBudget, log: logging.Logger) -> None:
        self._inner, self._budget, self._log = inner, budget, log

    async def chat(self, req: ChatRequest) -> ChatResponse:
        reserved = estimate_tokens(req)
        self._budget.reserve(reserved)           # no await between check and update: atomic
        actual, started = 0, time.perf_counter()
        try:
            resp = await self._inner.chat(req)
            actual = resp.usage.prompt_tokens + resp.usage.completion_tokens
            self._log.info(json.dumps({
                "event": "llm_call", "model": resp.model, "request_id": resp.id,
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
                "cost_usd": round(cost_usd(resp.model, resp.usage), 8),
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            }))
            return resp
        finally:
            self._budget.settle(reserved, actual)
```

Running this around a fake provider that reports 100 prompt and 20 completion tokens logs `"cost_usd": 2.7e-05` (the latency field varies), leaves the budget at `TokenBudget(limit=1000, used=120, reserved=0)`, and a following request that needs 1,004 tokens is rejected with `blocked: need 1004, have 880`. Note the trade-off in `finally`: if the call fails or is cancelled, you settle with zero, yet the provider may still have billed generated tokens. Decide per system whether to charge the reservation instead; erring towards the reservation is the safer default for hard budgets.

With an official SDK (illustrative, check current docs) the same concerns map to constructor options, for example `AsyncOpenAI(timeout=30.0, max_retries=2)` and `await client.chat.completions.create(...)`, or `AsyncAnthropic` with `await client.messages.create(...)`. SDK retries are convenient but opaque: you still need your own deadline, budget and logging, and you must not stack your retries on the SDK's (3 x 3 = 9 attempts).

### Testing with `MockTransport`

`httpx.MockTransport` takes a handler `(Request) -> Response` (sync or async), so the entire client runs in-process with no network. Combined with the injected `sleep` and a seeded `random.Random`, retry behaviour becomes a deterministic unit test. The tests below are plain async functions; run them under `pytest-asyncio` or `anyio`'s pytest plugin, or drive them with `asyncio.run` as shown.

```python
def ok_body(text="hi"):
    return {"id": "r1", "model": "small-model",
            "choices": [{"message": {"role": "assistant", "content": text},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 3}}

REQ = ChatRequest(model="small-model", messages=[Message(role="user", content="ping")])


async def test_retries_429_then_503_then_ok():
    calls, keys = [], []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        keys.append(request.headers["idempotency-key"])
        if len(calls) == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})
        if len(calls) == 2:
            return httpx.Response(503)
        return httpx.Response(200, json=ok_body())

    sleeps: list[float] = []

    async def fake_sleep(s: float) -> None:
        sleeps.append(s)

    client = HttpChatClient("https://llm.test", "k", transport=httpx.MockTransport(handler),
                            sleep=fake_sleep, rng=random.Random(0))
    async with client:
        resp = await client.chat(REQ)
    print(resp.text, len(calls), len(set(keys)), [round(s, 3) for s in sleeps])
    assert sleeps[0] == 2.0 and 0 <= sleeps[1] <= 1.0


async def test_deadline():
    async def slow(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(5)
        return httpx.Response(200, json=ok_body())

    async with HttpChatClient("https://llm.test", "k", transport=httpx.MockTransport(slow)) as c:
        try:
            async with asyncio.timeout(0.05):
                await c.chat(REQ)
        except TimeoutError:
            print("deadline exceeded")
```

The first test prints `hi 3 1 [2.0, 0.758]`: three HTTP calls, one distinct idempotency key, a first delay of exactly the `Retry-After` value (2.0) and a second delay inside the jitter window. Against the same client, a 400 is attempted once, persistent 500s stop after 4 calls, two `httpx.ConnectError`s then a 200 succeed on call 3, and a stream without `[DONE]` yields `['Hel']` and then raises. The second test prints `deadline exceeded`.

> **Interview tip:** When asked "how do you make an LLM client robust", structure the answer as timeouts (per phase and total), retry classification, backoff with jitter plus `Retry-After`, idempotency, streaming edge cases, budgets, and observability, then say how you test each with an injected transport and clock.

## Practical Backend Scenario

You run an LLM gateway for a support-automation product with 40 tenants. At 09:00 every weekday a batch job fans out 5,000 summarisation calls; the provider starts returning 429 with `Retry-After: 4`. The first version of your client slept a fixed two seconds and retried up to ten times, so the herd re-arrived in lockstep, the 429 rate climbed, and the same batch was billed twice when read timeouts caused duplicates. The fix is the design in this lesson: bounded concurrency with a semaphore, full-jitter backoff that respects `Retry-After`, a stable idempotency key per logical summary, a per-tenant token budget with reserve and settle, and a structured cost log keyed by tenant and feature. After the change, retried calls stop colliding, duplicate billing disappears, and finance can see which tenant spent what.

## Practice Loop

1. Type out the models, `RetryPolicy`, `parse_retry_after` and `HttpChatClient.chat`. Run the `MockTransport` test and confirm you get three calls, one key and a first sleep of exactly the `Retry-After` value.
2. Add a test where the server sends `Retry-After: 120` and show the client fails fast with `LLMError` instead of sleeping.
3. Add `stream()` and `iter_sse_data`. Feed it an event split across two `data:` lines and a keep-alive comment, and assert the joined payload.
4. Wrap `chat` in `MeteredProvider`, run ten concurrent calls with `asyncio.gather` against a fake, and assert the budget never goes negative.
5. Consume `stream()` with `contextlib.aclosing`, break after the first token, and confirm that the generator's cleanup has run before the next statement executes. Then repeat without `aclosing` and observe the difference.
6. Replace the fixed jitter source with a seeded `random.Random` and show two runs produce identical sleep lists.

## Evidence of Understanding

- I can state which of connect, read, write and pool a given hang belongs to, and why a read timeout does not bound a stream's total duration.
- I can justify the retry set (429, 5xx, connect and read errors) and name three status codes that must not be retried.
- I can explain full jitter and why `Retry-After` is combined with backoff using `max`, not replaced by it.
- I can explain why a retried POST needs an idempotency key and what changes if the provider ignores it.
- I can describe when a stream can and cannot be retried, and how to detect truncation.
- I can write a `Protocol`-based provider abstraction and a decorator that meters cost.

## Interview Questions to Rehearse

### Q: Walk me through how you would retry LLM API calls.
Classify first: retry 429, 500, 502, 503, 504 and connection-level failures; fail immediately on other 4xx because they are deterministic. Use exponential backoff with full jitter so throttled clients de-synchronise, take the maximum of that and the server's `Retry-After`, cap attempts and total deadline, and attach one idempotency key per logical call so a retry after a read timeout cannot double-bill. Log every retry with the reason, because retry storms are a leading cause of incidents.

### Q: Why is a read timeout different for streaming and non-streaming calls?
The read timeout is the maximum wait for the next chunk, not the call duration. A non-streaming completion sends nothing until generation finishes, so the read timeout must cover the slowest valid generation. A stream sends tokens continuously, so the same setting acts as a stall detector, and the overall duration needs a separate deadline such as `asyncio.timeout`.

### Q: A client disconnects halfway through a streamed answer. What should your service do?
Stop the upstream call. Propagate cancellation so the `async with` around the upstream stream exits and closes the connection, which lets the provider stop generating. Otherwise you pay for and hold a connection for tokens nobody receives. Record the partial usage, since cancelled generations can still be billed.

### Q: How do you enforce a per-tenant token budget under concurrency?
Estimate the worst case before the call (prompt estimate plus `max_tokens`), reserve it atomically, make the call, and settle with the provider-reported usage afterwards. Atomicity matters: with check-then-await-then-update, concurrent requests all pass the check. In a multi-process deployment the counter lives in Redis or a database with an atomic increment, not in process memory.

### Q: Should you use the vendor SDK or raw `httpx`?
SDKs give typed models, streaming helpers and sane defaults, which is the right starting point. Raw `httpx` gives control and a vendor-neutral seam. Either way, I put my own `Protocol` boundary in front, set an explicit total deadline, avoid double retry layers, and keep cost and latency logging in my own code so I can swap providers.

## Common Pitfalls

- Using one global `httpx.Timeout(None)` or the default for everything: requests hang, or streams die at an arbitrary five seconds.
- Retrying every exception, including `ValidationError` from a malformed response or 400s: infinite loops and a larger bill.
- Fixed or un-jittered backoff, which produces synchronised retry waves.
- Generating a fresh idempotency key inside the retry loop, which defeats deduplication.
- Creating `httpx.AsyncClient()` inside the request handler instead of once per process, losing connection reuse and leaking sockets.
- Treating a stream that ended without the final sentinel as a successful answer.
- Catching `BaseException` (or using a bare `except:`) in async code, which swallows `CancelledError` and breaks deadlines.
- Counting tokens only after the call, so budget enforcement happens after the money is spent.
- Stacking SDK retries under your own retries.

## Suggested Extension

Add a `FallbackProvider` that wraps a primary and a secondary `ChatProvider`, with a circuit breaker: after N consecutive failures in a rolling window it opens and routes straight to the secondary for 30 seconds, then half-opens with a single probe request. Test the open, half-open and closed transitions with `MockTransport` and an injected clock.
