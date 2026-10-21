# Error Handling, Logging and Resilience

Every integration with an LLM vendor, payment provider or queue fails sometimes, so the question is what your service does next: retry in a way that heals the outage or amplifies it, log in a way that lets you debug at 3 a.m., and charge the customer once or twice. Senior interviews probe this with scenario questions ("the vendor starts returning 429s; walk me through it") because the right answer combines exceptions, logging, timeouts, backoff and idempotency into one coherent design.

## Concepts Covered

### Designing exception hierarchies and `raise ... from`

Give a service one base exception (`GatewayError`) so callers can catch "anything we raise on purpose" without a bare `except Exception`. Below it, model *what the caller should do*, not where the error came from: a `retryable` flag or separate classes for transient and permanent failures. Carry data on the exception (`retry_after`) instead of encoding it in the message string.

When you translate a low-level error into a domain one, use `raise New(...) from exc`. That sets `__cause__` and prints "The above exception was the direct cause of...". If you raise inside an `except` block without `from`, Python still chains implicitly via `__context__` ("During handling of the above exception, another exception occurred"), which reads like a bug in your error handler. `from None` suppresses the context when the original is noise. I ran the following:

```python
class GatewayError(Exception):
    """Base for everything this service raises on purpose."""


class UpstreamError(GatewayError):
    retryable = False


class UpstreamTimeout(UpstreamError):
    retryable = True


def call_vendor() -> None:
    raise TimeoutError("read timed out")


def complete() -> None:
    try:
        call_vendor()
    except TimeoutError as exc:
        raise UpstreamTimeout("vendor did not answer") from exc


try:
    complete()
except GatewayError as e:
    print(type(e).__name__, "| cause:", repr(e.__cause__), "| retryable:", e.retryable)
```

```text
UpstreamTimeout | cause: TimeoutError('read timed out') | retryable: True
```

Without `from`, `e.__cause__` is `None` but `e.__context__` still holds the original; with `from None`, `__suppress_context__` becomes `True` so the traceback hides it while `__context__` remains set. Never swallow with `except: pass`, and never catch `BaseException` (it includes `KeyboardInterrupt` and `asyncio.CancelledError`, which must propagate).

### `ExceptionGroup` and `except*` (3.11+)

Concurrent code can fail in several ways at once. `asyncio.TaskGroup` (3.11+) collects the failures of sibling tasks into an `ExceptionGroup`. `except*` matches subgroups by type, runs each matching handler at most once with a group containing only the matching exceptions, and re-raises whatever is unhandled as a new group. You cannot mix `except` and `except*` in one `try`, and a plain `except TimeoutError` will **not** catch a group that wraps one.

```python
import asyncio


async def vendor(name: str, fail: str | None) -> str:
    await asyncio.sleep(0)
    if fail == "t":
        raise TimeoutError(f"{name} timed out")
    if fail == "v":
        raise ValueError(f"{name} bad payload")
    return name


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(vendor("a", "t"))
            tg.create_task(vendor("b", "v"))
            tg.create_task(vendor("c", "t"))
            tg.create_task(vendor("d", None))
    except* TimeoutError as eg:
        print("timeouts:", [str(e) for e in eg.exceptions])
    except* ValueError as eg:
        print("value errors:", [str(e) for e in eg.exceptions])


asyncio.run(main())
```

```text
timeouts: ['a timed out', 'c timed out']
value errors: ['b bad payload']
```

A `TaskGroup` also cancels the remaining tasks when one fails, which is usually what you want for a fan-out where all results are required. If partial results are acceptable, wrap each task so it returns an outcome object instead of raising, or use `asyncio.gather(..., return_exceptions=True)`.

### `logging`: loggers, handlers, levels and `dictConfig`

The model: code asks for a logger by name (`logging.getLogger(__name__)`); records flow up the dotted hierarchy to handlers; a record must pass the logger's level, then each handler's level and filters. **Libraries** log with a named logger and add only a `NullHandler`; **applications** configure handlers once, at startup, ideally with `logging.config.dictConfig`. Pass arguments lazily (`log.info("charged %s", tenant)`) so formatting only happens if the record is emitted, use `log.exception(...)` inside an `except` block to attach the traceback, and set `disable_existing_loggers: False` or you silently disable loggers created before configuration.

### Structured logging with request context

JSON lines with stable keys can be queried; formatted prose cannot. Put request-scoped context (request id, tenant) into a `contextvars.ContextVar` and inject it with a `Filter`, so every log call in the request carries it without threading parameters through your code. `ContextVar` works across `await` points and per-task in asyncio, unlike a global or `threading.local`. I ran this configuration:

```python
import contextvars
import json
import logging
import logging.config

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True


class JsonFormatter(logging.Formatter):
    RESERVED = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "request_id"}

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": record.request_id,
        }
        payload.update({k: v for k, v in vars(record).items() if k not in self.RESERVED})
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info).splitlines()[-1]
        return json.dumps(payload, sort_keys=True)


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"ctx": {"()": ContextFilter}},
    "formatters": {"json": {"()": JsonFormatter}},
    "handlers": {"stdout": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout",
                            "formatter": "json", "filters": ["ctx"], "level": "INFO"}},
    "loggers": {"gateway": {"level": "DEBUG", "handlers": ["stdout"], "propagate": False}},
    "root": {"level": "WARNING", "handlers": ["stdout"]},
})

log = logging.getLogger("gateway.billing")
request_id.set("req-42")
log.debug("dropped: handler level is INFO")
log.info("charged tenant", extra={"tenant": "acme", "tokens": 1200})
try:
    1 / 0
except ZeroDivisionError:
    log.exception("charge failed", extra={"tenant": "acme"})
```

```text
{"level": "INFO", "logger": "gateway.billing", "msg": "charged tenant", "request_id": "req-42", "tenant": "acme", "tokens": 1200}
{"exc": "ZeroDivisionError: division by zero", "level": "ERROR", "logger": "gateway.billing", "msg": "charge failed", "request_id": "req-42", "tenant": "acme"}
```

> **Production note:** Never log prompts, API keys or personal data at INFO. Log identifiers and sizes (token counts, document ids), and make verbose payload logging an explicit, short-lived DEBUG switch.

### Retries: exponential backoff with jitter

Retry only what is **transient** (timeouts, 429, 502/503/504, connection resets) and **safe to repeat** (idempotent or protected by an idempotency key). Never retry 4xx validation errors. Backoff spreads load over time; **jitter** stops thousands of clients that failed together from retrying in lockstep (a thundering herd). "Full jitter" picks a random delay between 0 and the exponential cap. With a seeded generator I got these delays for attempts 0 to 5, against the un-jittered caps shown second:

```python
import random


def full_jitter(attempt: int, base: float = 0.5, cap: float = 20.0,
                rng: random.Random | None = None) -> float:
    """Uniform delay in [0, min(cap, base * 2**attempt)]."""
    r = rng or random
    return r.uniform(0, min(cap, base * 2 ** attempt))


rng = random.Random(7)
print([round(full_jitter(a, rng=rng), 2) for a in range(6)])
print([min(20.0, 0.5 * 2 ** a) for a in range(6)])
```

```text
[0.16, 0.15, 1.3, 0.29, 4.29, 5.85]
[0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
```

In production use `tenacity` instead of hand-rolling the loop. It supports async functions and keeps policy declarative:

```python
import logging

from tenacity import (
    before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential,
)

log = logging.getLogger("gateway.vendor")


@retry(
    retry=retry_if_exception_type(UpstreamTimeout),
    wait=wait_random_exponential(multiplier=0.5, max=20),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(log, logging.WARNING),
    reraise=True,                      # surface the real error, not tenacity.RetryError
)
async def complete(prompt: str) -> str: ...
```

Honour `Retry-After` when the server sends it. Cap total attempts **and** total elapsed time, and remember retry amplification: if three layers each retry three times, one user request becomes 27 vendor calls during an outage. Retry at one layer only.

### Timeouts and deadlines

Every network call needs a timeout; the default for many clients is "wait forever". Set separate connect and read timeouts on the HTTP client (`httpx.Timeout(10.0, connect=3.0)`), and bound the whole operation with `asyncio.timeout()` (3.11+), which raises `TimeoutError` and is preferred over `asyncio.wait_for` for composing with other code. Per-attempt timeouts plus an overall **deadline** prevent retries from outliving the user's patience:

```python
import asyncio


async def slow() -> None:
    await asyncio.sleep(10)


async def main() -> None:
    try:
        async with asyncio.timeout(0.05):
            await slow()
    except TimeoutError as e:
        print("asyncio.timeout ->", type(e).__name__)

    attempts = 0
    deadline = asyncio.get_running_loop().time() + 0.2
    try:
        async with asyncio.timeout_at(deadline):          # overall budget
            while True:
                attempts += 1
                try:
                    async with asyncio.timeout(0.05):     # per-attempt budget
                        await slow()
                except TimeoutError:
                    await asyncio.sleep(0.01)
    except TimeoutError:
        print("overall deadline hit; attempts >= 2:", attempts >= 2)


asyncio.run(main())
```

```text
asyncio.timeout -> TimeoutError
overall deadline hit; attempts >= 2: True
```

### Circuit breakers

When a dependency is down, retries make it worse and tie up your workers. A circuit breaker counts failures and, past a threshold, **opens**: calls fail immediately for a cool-down period. After the cool-down it goes **half-open** and lets one probe through; success closes the circuit, failure reopens it. Inject the clock so it is testable. I ran this with a threshold of 2 and a reset timeout of 10 seconds:

```python
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpen(Exception): ...


@dataclass
class CircuitBreaker:
    clock: Callable[[], float]
    failure_threshold: int = 3
    reset_timeout: float = 30.0
    _failures: int = 0
    _opened_at: float = 0.0
    state: State = State.CLOSED

    def call[R](self, fn: Callable[[], R]) -> R:
        if self.state is State.OPEN:
            if self.clock() - self._opened_at < self.reset_timeout:
                raise CircuitOpen("failing fast")
            self.state = State.HALF_OPEN
        try:
            result = fn()
        except Exception:
            self._failures += 1
            if self.state is State.HALF_OPEN or self._failures >= self.failure_threshold:
                self.state = State.OPEN
                self._opened_at = self.clock()
            raise
        self._failures = 0
        self.state = State.CLOSED
        return result
```

```python
now = 0.0
cb = CircuitBreaker(clock=lambda: now, failure_threshold=2, reset_timeout=10)


def boom() -> str:
    raise ConnectionError("down")


def ok() -> str:
    return "ok"


for step in ["boom", "boom", "ok", "wait", "ok"]:
    if step == "wait":
        now += 11
        print("t=11s")
        continue
    try:
        print(step, "->", cb.call(boom if step == "boom" else ok), cb.state.value)
    except CircuitOpen:
        print(step, "-> CircuitOpen", cb.state.value)
    except ConnectionError:
        print(step, "-> ConnectionError", cb.state.value)
```

```text
boom -> ConnectionError closed
boom -> ConnectionError open
ok -> CircuitOpen open
t=11s
ok -> ok closed
```

The sequence shows two failures opening the circuit, the next call failing fast without touching the vendor, and a probe after 11 seconds closing it. A real implementation also needs a lock (or a single event-loop owner) around state changes and a rule for how many concurrent probes are allowed in half-open.

### Idempotency keys

Retries and at-least-once queues deliver duplicates, so side effects need a deduplication key supplied by the caller (`Idempotency-Key` header, or a message id). Store the key with a hash of the request and the saved response; a repeat with the same key and payload returns the saved response, and a repeat with a **different** payload is a client bug that should be rejected. The in-memory version below is the idea; in production the "claim" must be atomic (a unique constraint insert, or Redis `SET key value NX EX ttl`) with an "in progress" state, otherwise two concurrent requests both pass the check and both charge.

```python
import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class IdempotencyStore:
    _done: dict[str, tuple[str, dict]] = field(default_factory=dict)

    def run(self, key: str, payload: dict, handler: Callable[[dict], dict]) -> dict:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if key in self._done:
            saved_digest, saved = self._done[key]
            if saved_digest != digest:
                raise ValueError("idempotency key reused with a different payload")
            return saved
        result = handler(payload)
        self._done[key] = (digest, result)
        return result
```

Calling `run("k1", {"amount": 500}, charge)` twice returned the same `{'charge_id': 'ch_1'}` and charged once; reusing `k1` with `{"amount": 900}` raised the mismatch error.

## Practical Backend Scenario

Your gateway calls a vendor LLM API. At 14:02 the vendor starts returning 503s. Without a design, each of 200 workers retries immediately three times, the vendor's recovery is delayed by your own traffic, requests pile up behind 60-second default timeouts, users double-submit, and a payment webhook is processed twice. With the design from this lesson: per-attempt timeouts and an overall deadline, jittered backoff only for retryable errors at one layer, a circuit breaker that fails fast and serves a degraded response, idempotency keys on the billing side effect, and structured logs carrying the request id so you can follow one request through all of it.

## Practice Loop

1. Build the `GatewayError` hierarchy with a `retryable` flag and a `RateLimited(retry_after)` subclass, and write tests for the translation from `TimeoutError` using `raise ... from`.
2. Run a `TaskGroup` with one failing task and one slow task. Verify the slow one is cancelled, and handle both `TimeoutError` and `ValueError` with `except*`.
3. Configure logging with `dictConfig`, JSON output and a `ContextVar` filter, and confirm two concurrent asyncio tasks log their own request ids.
4. Implement `full_jitter` and plot or print 1,000 delays for attempt 4 to see the distribution.
5. Wrap a flaky function with `tenacity` and a circuit breaker; use a fake clock and injected sleep to test the open, half-open and closed transitions.
6. Make the idempotency store concurrency-safe with an atomic claim (a `dict` plus lock, then a database unique constraint) and test with 20 concurrent callers.

## Evidence of Understanding

- I can explain the difference between `__cause__` and `__context__`, and when to use `from None`.
- I can predict which handler runs for an `ExceptionGroup` containing mixed exceptions, and why `except TimeoutError` does not catch it.
- I can configure logging so a library stays silent by default and an application gets JSON logs with request context.
- I can justify jitter, caps, retry budgets and single-layer retries with the thundering-herd and amplification failure modes.
- I can design an idempotent charge endpoint and say why the claim must be atomic.

## Interview Questions to Rehearse

### Q: When do you retry, and when not?

Retry transient failures (timeouts, connection errors, 429, 502/503/504) on operations that are idempotent or protected by an idempotency key. Do not retry validation errors or auth failures, and do not retry non-idempotent writes blindly. Use exponential backoff with jitter, honour `Retry-After`, and cap both attempts and total elapsed time.

### Q: Why add jitter to exponential backoff?

Without it, clients that failed together retry together, creating synchronized load spikes that keep a recovering service down. Randomizing each delay spreads the retries over the window. Full jitter (uniform between zero and the exponential cap) usually performs best.

### Q: Explain `raise X from Y` versus a bare `raise X` inside `except`.

`from Y` sets `__cause__`, an explicit "this error was caused by Y". A bare raise inside an `except` sets `__context__` implicitly, which prints as "during handling... another exception occurred" and signals a possible handler bug. `from None` suppresses the displayed context.

### Q: What is a circuit breaker and how does it differ from a retry?

A retry makes another attempt for one call. A breaker looks at the recent failure rate across calls, stops sending traffic to a failing dependency, and probes recovery after a cool-down. They complement each other: retries heal blips, breakers protect against sustained outages.

### Q: How do you make a payment endpoint safe against duplicate requests?

Require an idempotency key. Atomically claim it (unique insert or `SET NX`) together with a hash of the request, process once, store the response, and return the stored response on repeats. Reject the same key with a different payload and expire keys after a window.

### Q: How would you structure logging in an async service?

One `dictConfig` at startup, JSON output to stdout, `ContextVar`-backed filter adding request id and tenant, module-level loggers named `__name__`, lazy formatting, `log.exception` for errors, and no secrets or full prompts in logs.

## Common Pitfalls

- `except Exception: pass`, or catching `BaseException` and swallowing cancellation.
- Raising a new exception in an `except` block without `from`, hiding the intended cause.
- Calling `logging.basicConfig` in a library, or forgetting `disable_existing_loggers: False`.
- Formatting log messages with f-strings at DEBUG volume instead of lazy arguments.
- Retrying without jitter, without caps, or at several layers at once.
- Retrying non-idempotent operations without an idempotency key.
- No timeout (or only a read timeout) on outbound HTTP calls.
- Idempotency checks that read then write without an atomic claim.
- Treating `ExceptionGroup` like a normal exception in `except TimeoutError`.

## Suggested Extension

Build a `ResilientClient` that composes everything: per-attempt timeout, overall deadline, tenacity retries with `Retry-After` support, a shared circuit breaker, structured logs with the request id, and an idempotency key header. Test it against a fake vendor (an `httpx.MockTransport` handler) scripted to return 429, 503, timeouts and success, with an injected clock and sleep so the whole scenario runs in milliseconds.
