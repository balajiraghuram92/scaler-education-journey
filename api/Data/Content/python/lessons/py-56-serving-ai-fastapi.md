# Serving AI Features from FastAPI

Calling a model from a notebook is a solved problem. Serving it to thousands of users is not: responses take seconds and must stream, work can run for minutes, every request costs real money, one tenant can starve the others, and a prompt change can quietly make answers worse. FastAPI gives you the async plumbing, but the production concerns (disconnects, background work, caching, limits, tracing, evaluation and rollout) are yours to design. In AI and FDE interviews this is where "I built a demo" separates from "I ran it in production".

## Concepts Covered

### Streaming endpoints with SSE

For chat-style features, stream tokens as they are generated. Server-Sent Events (SSE) fit well: a one-way, text-based stream over plain HTTP that browsers consume with `EventSource` or `fetch` and that passes through most proxies. In FastAPI, return a `StreamingResponse` wrapping an async generator, with `media_type="text/event-stream"`, `Cache-Control: no-cache`, and `X-Accel-Buffering: no` so an nginx-style proxy does not buffer the stream.

Three rules matter. **Once the first byte is sent you cannot change the status code**, so a mid-stream failure must be reported as an in-band `event: error` message. **Always close the upstream provider stream** (use `contextlib.aclosing`), or you keep generating and paying for tokens nobody reads. And **never swallow `asyncio.CancelledError`**: when the client disconnects, the server stops the response task, and your generator's `finally` blocks must run and the cancellation must propagate.

```python
from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import aclosing

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()
closed: list[str] = []          # demo only: records when the upstream stream was closed


async def upstream_tokens(prompt: str) -> AsyncIterator[str]:
    """Stand-in for the provider stream (an httpx streaming response in real life)."""
    try:
        for word in ("Refunds", "take", "five", "days."):
            await asyncio.sleep(0.01)
            yield word + " "
    finally:
        closed.append(prompt)             # real code: the HTTP connection to the provider closes here


def sse(data: dict | str, event: str | None = None) -> bytes:
    payload = data if isinstance(data, str) else json.dumps(data)
    head = f"event: {event}\n" if event else ""
    return f"{head}data: {payload}\n\n".encode()


class ChatIn(BaseModel):
    prompt: str


@app.post("/chat/stream")
async def chat_stream(body: ChatIn) -> StreamingResponse:
    async def events() -> AsyncIterator[bytes]:
        try:
            async with aclosing(upstream_tokens(body.prompt)) as tokens:
                async for token in tokens:
                    yield sse({"delta": token})
            yield sse("[DONE]")
        except asyncio.CancelledError:
            raise                          # the client left: clean up (finally blocks) and propagate
        except Exception:
            yield sse({"message": "upstream failed"}, event="error")   # headers are gone: cannot send a 500

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},   # stop proxy buffering
    )
```

Using Starlette's `TestClient` against this app, the response is `200` with content type `text/event-stream; charset=utf-8` and `cache-control: no-cache`, and the non-empty lines are `data: {"delta": "Refunds "}`, `data: {"delta": "take "}`, `data: {"delta": "five "}`, `data: {"delta": "days. "}` and `data: [DONE]`. The `closed` list then contains `'p1'`: the upstream generator's cleanup ran. To check disconnects without a network, I drove the ASGI app directly, delivered an `http.disconnect` message after two body chunks, and saw `closed` grow to include `'p2'`. How the server notifies the app (cancelling the response task or raising an error on the next send) depends on the server and ASGI version, but the contract is the same: your `finally` blocks run.

> **Pitfall:** Buffering proxies and compression middleware can hold SSE data until the response ends, which looks like "streaming works locally but not in production". Disable buffering for the route, send periodic comment lines (`: ping`) as keep-alives, and test through the real ingress.

### Background jobs for long work

Anything that can exceed a request timeout (summarising a 200-page contract, batch classification, an agent run) should not hold an HTTP connection. The pattern: `POST` creates a job and returns `202 Accepted` with a `Location` header; the client polls `GET /jobs/{id}` (or receives a webhook or SSE updates). FastAPI's `BackgroundTasks` is for small work after the response is sent, and it runs in the same process, so it dies with the worker and has no retry. For durable work use a real queue and separate workers (Celery, RQ, Arq, or a cloud queue). The in-process runner below shows the shape, including the details people forget: hold strong references to tasks (the event loop keeps only weak ones), bound concurrency with a semaphore, and scope job reads to the tenant.

```python
import time
import uuid
from dataclasses import dataclass
from typing import Literal

from fastapi import HTTPException
from fastapi.responses import JSONResponse


@dataclass(slots=True)
class Job:
    id: str
    tenant: str
    status: Literal["queued", "running", "done", "failed"] = "queued"
    result: str | None = None
    error: str | None = None


class JobRunner:
    """In-process job runner. Fine for a demo; production work belongs on a durable queue."""

    def __init__(self, max_concurrent: int = 2) -> None:
        self.jobs: dict[str, Job] = {}
        self._tasks: set[asyncio.Task[None]] = set()     # strong refs: the loop keeps only weak ones
        self._sem = asyncio.Semaphore(max_concurrent)

    def submit(self, tenant: str, work) -> Job:
        job = Job(id=uuid.uuid4().hex[:8], tenant=tenant)
        self.jobs[job.id] = job
        task = asyncio.create_task(self._run(job, work))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return job

    async def _run(self, job: Job, work) -> None:
        async with self._sem:                            # bound concurrent LLM-heavy jobs
            job.status = "running"
            try:
                job.result = await work()
                job.status = "done"
            except Exception as exc:
                job.status, job.error = "failed", type(exc).__name__

    async def shutdown(self) -> None:
        for t in list(self._tasks):
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)


runner = JobRunner()


class SummariseIn(BaseModel):
    tenant: str
    document_id: str
    fail: bool = False


@app.post("/summaries", status_code=202)
async def create_summary(body: SummariseIn) -> JSONResponse:
    async def work() -> str:
        await asyncio.sleep(0.05)                        # stands in for a multi-minute map-reduce summary
        if body.fail:
            raise RuntimeError("provider down")
        return f"summary of {body.document_id}"

    job = runner.submit(body.tenant, work)
    return JSONResponse({"job_id": job.id, "status": job.status},
                        status_code=202, headers={"Location": f"/summaries/{job.id}"})


@app.get("/summaries/{job_id}")
async def get_summary(job_id: str, tenant: str) -> dict:
    job = runner.jobs.get(job_id)
    if job is None or job.tenant != tenant:               # same 404 for 'missing' and 'someone else's'
        raise HTTPException(404, "job not found")
    return {"job_id": job.id, "status": job.status, "result": job.result, "error": job.error}
```

Run under `TestClient` (as a context manager, so the event loop keeps running between calls), the POST returns `202`, a `Location` header starting `/summaries/` and status `queued`; polling shows the status move through `running` to `done` with `summary of doc-9`; the same job id with another tenant returns `404`; a job created with `fail=True` ends as `failed` with error `RuntimeError`. Expose the shutdown through the application lifespan so in-flight jobs are cancelled cleanly, and in production persist job state so a restart does not lose it.

### Caching: exact and semantic

LLM calls are expensive and slow, and many requests repeat. Cache at two levels.

**Exact response cache.** Key on everything that affects the output: tenant, prompt version, model, normalised messages and sampling parameters. Cache only when the call is deterministic enough (temperature 0 or a stable template) and the content is not personalised or time-sensitive, and give entries a TTL. Putting the tenant in the key prevents cross-tenant leakage; putting the prompt version in the key means a prompt release naturally invalidates old answers.

**Semantic cache.** Embed the query, and return a stored answer when a previous query in the same tenant partition is similar enough. It raises hit rates for paraphrases, but similarity is not equivalence: "reset my password" and "reset my colleague's password" are close in embedding space yet need different answers. Use a conservative threshold, restrict it to low-risk FAQ-style intents, partition by tenant, never cache personalised answers, and measure false-hit rate on labelled pairs before enabling it.

```python
import hashlib
import math
import re
from collections.abc import Callable
from typing import Annotated

import numpy as np
from fastapi import Depends, Header


def cache_key(tenant: str, prompt_version: str, model: str, messages: list[dict[str, str]],
              temperature: float) -> str:
    blob = json.dumps({"t": tenant, "pv": prompt_version, "m": model, "msgs": messages, "temp": temperature},
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


class TTLCache:
    def __init__(self, ttl_s: float, clock: Callable[[], float]) -> None:
        self._ttl, self._clock = ttl_s, clock
        self._data: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> str | None:
        item = self._data.get(key)
        if item is None or item[0] < self._clock():
            self._data.pop(key, None)
            return None
        return item[1]

    def put(self, key: str, value: str) -> None:
        self._data[key] = (self._clock() + self._ttl, value)


def embed(text: str, dim: int = 128) -> np.ndarray:
    """Toy embedding (hashed bag of words). Real systems call an embedding model."""
    v = np.zeros(dim, dtype=np.float32)
    for tok in re.findall(r"[a-z0-9]+", text.lower()):
        h = int.from_bytes(hashlib.blake2b(tok.encode(), digest_size=8).digest(), "big")
        v[h % dim] += 1.0
    n = float(np.linalg.norm(v))
    return v / n if n else v


class SemanticCache:
    def __init__(self, threshold: float = 0.8) -> None:
        self.threshold = threshold
        self._vecs: dict[str, list[np.ndarray]] = {}       # per-tenant partitions
        self._answers: dict[str, list[str]] = {}

    def lookup(self, tenant: str, query: str) -> tuple[str, float] | None:
        vecs = self._vecs.get(tenant)
        if not vecs:
            return None
        sims = np.stack(vecs) @ embed(query)
        i = int(np.argmax(sims))
        return (self._answers[tenant][i], float(sims[i])) if sims[i] >= self.threshold else None

    def store(self, tenant: str, query: str, answer: str) -> None:
        self._vecs.setdefault(tenant, []).append(embed(query))
        self._answers.setdefault(tenant, []).append(answer)
```

The key is stable for identical inputs (`True`) but differs for another tenant or another prompt version (`False False`). A cached value is returned until its TTL passes and `None` afterwards. With the toy embedding, after storing "how do I reset my password", the query "how can I reset my password" hits with similarity `0.87`, "password reset how do I" hits with `0.94`, "how do I delete my account" misses, another tenant misses, and the risky "how do I reset my colleagues password" also hits with `0.94`, which is exactly the false-hit danger described above.

### Per-tenant rate limits and cost controls

In a multi-tenant product the failure mode is a noisy neighbour: one tenant's batch job exhausts your provider quota and everyone gets 429s. Defend in layers. A **token-bucket rate limiter per tenant** smooths bursts and returns `429` with `Retry-After`. A **concurrency cap** limits simultaneous in-flight LLM calls per tenant. A **spend guard** enforces a daily or monthly budget, checking an estimate before the call (reserve) and recording the provider-reported usage after. Return different error codes in the body for "rate limited" versus "budget exhausted" so clients can react correctly. In a multi-process deployment, counters live in Redis or a database with atomic operations; in-process dictionaries only work for a single worker.

```python
class TenantLimiter:
    """Token bucket per tenant: `rate` tokens/second refill, `burst` capacity."""

    def __init__(self, rate: float, burst: float, clock: Callable[[], float]) -> None:
        self.rate, self.burst, self._clock = rate, burst, clock
        self._state: dict[str, tuple[float, float]] = {}      # tenant -> (tokens, last_ts)

    def take(self, tenant: str, cost: float = 1.0) -> float:
        """Return 0.0 if allowed, else the seconds to wait."""
        now = self._clock()
        tokens, last = self._state.get(tenant, (self.burst, now))
        tokens = min(self.burst, tokens + (now - last) * self.rate)
        if tokens >= cost:
            self._state[tenant] = (tokens - cost, now)
            return 0.0
        self._state[tenant] = (tokens, now)
        return (cost - tokens) / self.rate


class SpendGuard:
    def __init__(self, daily_budget_usd: float) -> None:
        self.budget = daily_budget_usd
        self.spent: dict[str, float] = {}

    def check(self, tenant: str, estimate_usd: float) -> bool:
        return self.spent.get(tenant, 0.0) + estimate_usd <= self.budget

    def record(self, tenant: str, actual_usd: float) -> None:
        self.spent[tenant] = self.spent.get(tenant, 0.0) + actual_usd


now = [0.0]                                                    # injectable clock for tests
limiter = TenantLimiter(rate=1.0, burst=2, clock=lambda: now[0])
spend = SpendGuard(daily_budget_usd=0.01)


def tenant_id(x_tenant_id: Annotated[str, Header()]) -> str:
    return x_tenant_id


def enforce_limits(tenant: Annotated[str, Depends(tenant_id)]) -> str:
    wait = limiter.take(tenant)
    if wait > 0:
        raise HTTPException(429, "rate limit exceeded", headers={"Retry-After": str(math.ceil(wait))})
    if not spend.check(tenant, estimate_usd=0.004):
        raise HTTPException(429, "daily budget exhausted")
    return tenant


@app.post("/chat")
async def chat(body: ChatIn, tenant: Annotated[str, Depends(enforce_limits)]) -> dict:
    spend.record(tenant, 0.004)                               # real code records provider-reported usage
    return {"tenant": tenant, "answer": "ok"}
```

Three quick calls for tenant `acme` give `[200, 200, 429]` (burst of 2), and the fourth is `429` with `Retry-After: 1` and detail `rate limit exceeded`. Advancing the fake clock to 5 seconds refills the bucket, but the two earlier calls spent `0.008` of the `0.01` budget, so the next call is `429` with `daily budget exhausted`, as is the one after. A different tenant gets `200`, and a request without the `X-Tenant-Id` header gets `422`. Dependencies make this reusable (`dependencies=[Depends(enforce_limits)]` on a router), and taking identity from an authenticated token rather than a client-supplied header is what you would do in production.

### Tracing and metrics for LLM calls

LLM latency is dominated by the provider and varies widely, so you need per-call visibility: which model, which prompt version, how many tokens, how long, did it fail. Use OpenTelemetry spans for individual requests (with request ids that link logs, traces and the provider's own request id) and metrics for aggregates: a latency histogram, token counters, error counts, cache hit rate. Keep metric labels low-cardinality (model, prompt version, outcome) and put high-cardinality values such as tenant or request id on spans and logs. OpenTelemetry's GenAI semantic conventions define attribute names such as `gen_ai.request.model` and `gen_ai.usage.input_tokens`; they were still evolving at the time of writing, so check the current specification. For streaming, also record time to first token, since total duration hides what the user feels.

```python
from opentelemetry import metrics, trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("llm-gateway")
meter = metrics.get_meter("llm-gateway")
latency_ms = meter.create_histogram("llm.request.duration", unit="ms")
tokens_total = meter.create_counter("llm.tokens", unit="{token}")


async def traced_chat(p, model: str, prompt: str, tenant: str, prompt_version: str):
    with tracer.start_as_current_span("llm.chat") as span:
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("app.tenant", tenant)                 # fine on spans, risky as a metric label
        span.set_attribute("app.prompt_version", prompt_version)
        started = time.perf_counter()
        attrs = {"model": model, "prompt_version": prompt_version}
        try:
            resp = await p.chat(model, prompt)
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR))
            latency_ms.record((time.perf_counter() - started) * 1000, {**attrs, "outcome": "error"})
            raise
        span.set_attribute("gen_ai.usage.input_tokens", resp.prompt_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", resp.completion_tokens)
        latency_ms.record((time.perf_counter() - started) * 1000, {**attrs, "outcome": "ok"})
        tokens_total.add(resp.prompt_tokens, {**attrs, "kind": "input"})
        tokens_total.add(resp.completion_tokens, {**attrs, "kind": "output"})
        return resp
```

With the OpenTelemetry SDK's in-memory exporters wired up and a fake provider (one success reporting 120 input and 30 output tokens, one `TimeoutError`), I got two `llm.chat` spans, the first with unset (OK) status and the token attributes, the second with status `ERROR`; the histogram had one data point for `outcome=ok` and one for `outcome=error`, and the token counter held `120` for `kind=input` and `30` for `kind=output`. In production you replace the in-memory exporters with an OTLP exporter and the FastAPI instrumentation package so HTTP spans become parents of the LLM spans.

### Evaluation in CI

Treat prompts and model choices as code that needs tests. Keep a golden set of representative cases, including adversarial ones (prompt extraction, out-of-policy requests). Start with deterministic checks (must contain, must not contain, length, JSON validity) because they are cheap, explainable and stable; add LLM-as-judge scoring for subjective qualities, calibrated against human labels. Run a mocked or recorded version on every pull request and the live-model version on a schedule or before release, since live runs cost money and are non-deterministic, so compare pass rates with a tolerance rather than expecting identical outputs.

```python
import re
from collections.abc import Awaitable
from dataclasses import dataclass

Generate = Callable[[str], Awaitable[str]]


@dataclass(frozen=True)
class EvalCase:
    question: str
    must_contain: tuple[str, ...]          # deterministic checks first: cheap, stable, explainable
    must_not_contain: tuple[str, ...] = ()
    max_words: int = 60


def passes(case: EvalCase, answer: str) -> bool:
    low = answer.lower()
    return (all(s.lower() in low for s in case.must_contain)
            and not any(s.lower() in low for s in case.must_not_contain)
            and len(re.findall(r"\S+", answer)) <= case.max_words)


async def pass_rate(generate: Generate, cases: list[EvalCase], concurrency: int = 4) -> float:
    sem = asyncio.Semaphore(concurrency)

    async def one(case: EvalCase) -> bool:
        async with sem:
            return passes(case, await generate(case.question))

    results = await asyncio.gather(*(one(c) for c in cases))
    return sum(results) / len(results)


def fake(answers: dict[str, str]) -> Generate:        # canned answers standing in for the model
    async def generate(q: str) -> str:
        return answers[q]
    return generate


CASES: list[EvalCase] = [...]                         # your golden set; five cases in the run below
BASELINE, TOLERANCE = 1.0, 0.0


def release_gate(answers) -> str:
    rate = asyncio.run(pass_rate(fake(answers), CASES))
    verdict = "PASS" if rate >= BASELINE - TOLERANCE else "FAIL"
    return f"{verdict} pass_rate={rate:.2f} (baseline {BASELINE:.2f})"
```

With five cases (refund timing, the 90-day policy, the API rate limit, a system-prompt extraction attempt and an SSO question) and canned answers standing in for the model, prompt version 3 prints `PASS pass_rate=1.00 (baseline 1.00)`. Prompt version 4, which stops naming the Enterprise plan and leaks the system prompt when asked, prints `FAIL pass_rate=0.60 (baseline 1.00)`. In CI that assertion fails the pull request (`assert rate >= BASELINE - TOLERANCE`), and the failing cases are the diagnostic.

### Safe rollout of prompt and model versions

A prompt or model change is a deployment. Version them (a prompt version string stored with every log line, cache key and trace), keep the previous version deployable, and release gradually. **Sticky percentage rollout:** hash a stable id (tenant or user) together with the experiment name into a bucket from 0 to 99, so a given tenant always sees the same variant and raising the percentage only adds tenants. **Shadow mode:** run the candidate on a sample of live traffic, discard its output, and compare cost, latency and offline-scored quality. **Rollback:** a configuration flag, not a redeploy. Watch the guardrail metrics (error rate, p95 latency, cost per request, refusal rate, thumbs-down rate) during each step and have an automatic halt.

```python
def variant_for(tenant: str, experiment: str, rollout_pct: int) -> Literal["stable", "candidate"]:
    bucket = int(hashlib.sha256(f"{experiment}:{tenant}".encode()).hexdigest()[:8], 16) % 100
    return "candidate" if bucket < rollout_pct else "stable"
```

For 1,000 tenants the candidate share at 0, 10, 50 and 100 percent is `{0: 0, 10: 101, 50: 527, 100: 1000}`, the same tenant always gets the same variant, and every tenant in the 10 percent group is also in the 50 percent group, so widening the rollout never flips anyone back.

> **Interview tip:** Describe release safety as a pipeline: offline eval gate, shadow traffic, sticky percentage rollout with guardrail metrics, instant rollback. It shows you treat prompts as production artefacts.

## Practical Backend Scenario

Your company ships an "ask the docs" assistant to 60 enterprise tenants. Launch week brings four incidents: a nginx ingress buffers the SSE stream so answers appear all at once; a tenant's 5,000-document import runs as a single request and times out at 60 seconds; one tenant's nightly script consumes 70 percent of the provider quota and everyone else sees 429s; and a prompt tweak that "sounds friendlier" drops accuracy on policy questions without anyone noticing for nine days. The fixes map one-to-one onto this lesson: disable proxy buffering and add keep-alives, move imports to a `202` job with a queue and status endpoint, add a per-tenant token bucket with daily spend caps, and add a CI evaluation gate plus a sticky 10 percent rollout with shadow comparison. Dashboards show p95 time to first token, cost per tenant, cache hit rate and the eval pass rate per prompt version.

## Practice Loop

1. Build the SSE endpoint, call it with `TestClient.stream`, and assert the exact `data:` lines and headers.
2. Wrap the upstream generator in `aclosing`, then drive the app with a raw ASGI `http.disconnect` and assert that the upstream cleanup ran.
3. Implement the job runner and test the full lifecycle: `202`, `running`, `done`, tenant isolation (`404`) and a failing job.
4. Implement `cache_key` and `TTLCache` with a fake clock. Show that changing tenant or prompt version changes the key.
5. Add the semantic cache and build a 20-pair labelled set to measure the false-hit rate at thresholds 0.7, 0.8 and 0.9.
6. Implement the token bucket and spend guard as dependencies; test burst, refill, `Retry-After`, tenant isolation and budget exhaustion with an injected clock.
7. Add OpenTelemetry spans and metrics with in-memory exporters and assert the attributes and counters.
8. Write the golden-set gate and prove that a worse prompt fails it.

## Evidence of Understanding

- I can explain why a streaming error cannot change the HTTP status and what to send instead.
- I can explain what must happen when a client disconnects mid-stream, and why swallowing `CancelledError` breaks it.
- I can say when `BackgroundTasks` is enough and when a durable queue is required.
- I can design an exact cache key and justify a semantic cache threshold and its failure mode.
- I can describe a per-tenant token bucket, a spend guard and the right status codes and headers.
- I can name the metrics and span attributes I would record per LLM call and which labels to avoid.
- I can describe an evaluation gate in CI and a sticky, reversible rollout.

## Interview Questions to Rehearse

### Q: How do you stream an LLM response from FastAPI, and what can go wrong?
Return a `StreamingResponse` over an async generator with the `text/event-stream` media type and anti-buffering headers. Failure cases: a proxy buffering the stream; an error after the first byte, which must be sent as an in-band event because the status is already 200; the client disconnecting, which must close the upstream provider stream so you stop paying for tokens; and swallowing cancellation so cleanup never runs.

### Q: A request takes five minutes. How do you design the API?
Make it asynchronous: `POST` validates and enqueues a job, returns `202` with a job id and `Location`; workers process it from a durable queue with retries and concurrency limits; clients poll a status endpoint or get a webhook. Job state is persisted and scoped to the tenant, results have an expiry, and the job is idempotent so a retried delivery cannot duplicate side effects.

### Q: Would you add a semantic cache?
Only with measurement and constraints. It helps for repetitive FAQ-style traffic, but embedding similarity is not equivalence, so I partition by tenant, exclude personalised or high-risk intents, set a high threshold, log hits and sample them for review, and track the false-hit rate on labelled pairs. An exact-match cache keyed by tenant, prompt version, model and parameters is the safer first step.

### Q: How do you stop one tenant from hurting the others or blowing the budget?
Per-tenant token buckets for request rate, per-tenant concurrency caps, and a budget guard that reserves an estimated cost before the call and records actual usage afterwards. Return `429` with `Retry-After` for rate limits and a distinct error code for budget exhaustion. State lives in Redis or the database so limits hold across workers, and quotas are alertable before they bite.

### Q: How do you release a new prompt safely?
Version it and run the golden-set evaluation in CI as a gate. Then shadow-run it on live traffic, roll out to a sticky percentage of tenants chosen by hashing, watch error rate, latency, cost and quality signals, and keep rollback as a configuration change. The prompt version is attached to logs, traces and cache keys so any regression is attributable.

## Common Pitfalls

- Letting a proxy or compression middleware buffer the SSE stream, then blaming FastAPI.
- Catching `Exception` or `BaseException` in a streaming generator so disconnect cleanup never runs.
- Not closing the upstream provider stream when the client disconnects.
- Using `BackgroundTasks` for work that must survive a restart or be retried.
- Creating `asyncio.create_task` without keeping a reference, so the task can be garbage collected mid-run.
- Cache keys missing tenant, prompt version or sampling parameters, which leak data or serve stale answers.
- A semantic cache with a low threshold, or on personalised intents.
- Global rate limits only, so the loudest tenant starves the rest.
- High-cardinality metric labels (tenant id, request id) that explode your metrics bill.
- Releasing a prompt change with no evaluation gate, no versioning and no rollback path.

## Suggested Extension

Add time-to-first-token and tokens-per-second metrics to the streaming endpoint, then build a small k6 or Locust load test that opens 200 concurrent SSE streams across 20 tenants, with one deliberately noisy tenant. Verify that the noisy tenant is throttled, the others keep a flat p95 time to first token, and that cancelling the clients leaves no orphaned upstream connections.
