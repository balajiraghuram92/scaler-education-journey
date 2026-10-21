# Running FastAPI in Production

A FastAPI app that passes its tests is about 30% of a service. The rest is what happens at 2 a.m.: a request fails and nobody can find its logs, a deploy drops in-flight LLM calls, a background job silently disappears with a restarted pod, or four workers each open their own connection pool and starve the database. Interviewers for AI and FDE roles ask how you would operate the thing, because customers judge you on the incidents, not the endpoints.

## Concepts Covered

### Middleware versus dependencies

Use a **dependency** when the logic needs the request's typed data, can differ per route, or should be overridable in tests: authentication, tenant resolution, pagination, per-route rate limits. Use **middleware** for cross-cutting behaviour that applies to every request including unmatched routes and errors, and works on raw bytes and headers: request IDs, timing, security headers, access logging.

Middleware choice matters. `@app.middleware("http")` and `BaseHTTPMiddleware` wrap the app in extra tasks and streams. They are convenient, but they have well-known limits: context variables set inside the endpoint are not visible after `call_next` returns, streaming and cancellation behave less predictably, and every request pays extra overhead. For anything hot, write a **pure ASGI middleware**: a class with `__init__(self, app)` and `async def __call__(self, scope, receive, send)`.

```python
import asyncio
import contextvars
import uuid

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class RequestContextMiddleware:
    """Pure ASGI middleware: no BaseHTTPMiddleware, so streaming and contextvars behave."""

    def __init__(self, app, header: bytes = b"x-request-id") -> None:
        self.app = app
        self.header = header

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(self.header, b"").decode()
        rid = incoming or uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)

        async def send_with_id(message) -> None:
            if message["type"] == "http.response.start":
                message = {**message, "headers": [*message.get("headers", []), (self.header, rid.encode())]}
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            request_id_var.reset(token)


async def inner_app(scope, receive, send) -> None:
    print("inner sees request_id =", request_id_var.get())
    await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"ok"})


async def main() -> None:
    sent = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    app = RequestContextMiddleware(inner_app)
    await app({"type": "http", "method": "GET", "path": "/", "headers": [(b"x-request-id", b"abc-123")]}, receive, send)
    print(sent[0]["status"], dict(sent[0]["headers"])[b"x-request-id"].decode())
    print("after request:", request_id_var.get())


asyncio.run(main())
```

Output:

```text
inner sees request_id = abc-123
200 abc-123
after request: -
```

The ID arrives from the caller (or is generated), is visible to everything running inside the request, is echoed in the response, and is reset afterwards. Register it with `app.add_middleware(RequestContextMiddleware)`. Because the last middleware added is the outermost, add this one late enough that it wraps the others you want covered.

### Error handling and problem+json

Clients of a platform deserve one error shape. RFC 9457 (which obsoletes RFC 7807) defines `application/problem+json` with `type`, `title`, `status`, `detail` and `instance`, plus extension members. Raise domain exceptions from services and translate them in one place with `@app.exception_handler`; also override handlers for `RequestValidationError` and Starlette's `HTTPException` so even framework-generated errors use the same envelope.

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM = "application/problem+json"


class DomainError(Exception):
    status = 400
    type_ = "https://errors.example.com/domain-error"
    title = "Domain error"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class BudgetExceeded(DomainError):
    status = 429
    type_ = "https://errors.example.com/budget-exceeded"
    title = "Token budget exceeded"


def problem(request: Request, status: int, title: str, detail: str, type_: str = "about:blank", **extra) -> JSONResponse:
    body = {"type": type_, "title": title, "status": status, "detail": detail, "instance": str(request.url.path), **extra}
    return JSONResponse(body, status_code=status, media_type=PROBLEM)


app = FastAPI()


@app.exception_handler(DomainError)
async def domain_handler(request: Request, exc: DomainError) -> JSONResponse:
    return problem(request, exc.status, exc.title, exc.detail, exc.type_)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"loc": list(e["loc"]), "msg": e["msg"]} for e in exc.errors()]
    return problem(request, 422, "Validation failed", "Request body or parameters are invalid.", errors=errors)


@app.exception_handler(StarletteHTTPException)
async def http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return problem(request, exc.status_code, "HTTP error", str(exc.detail))


class Chat(BaseModel):
    prompt: str
    max_tokens: int


@app.post("/chat")
async def chat(body: Chat):
    if body.max_tokens > 100:
        raise BudgetExceeded("tenant acme has 40 tokens left today")
    return {"ok": True}
```

Driving this with `TestClient`, a call with `max_tokens=500` returns `429 application/problem+json` with `"title": "Token budget exceeded"`, a body missing `max_tokens` returns `422` with `"errors": [{"loc": ["body", "max_tokens"], "msg": "Field required"}]`, and an unknown path returns `404` in the same envelope. Two production notes: validation errors can echo user input, so never put raw request bodies into `detail`; and an unhandled `Exception` is caught by Starlette's outermost error layer, which returns a bare `500` and re-raises so your server logs the traceback. Log it with the request ID, return a generic message, and never leak stack traces to clients.

### Structured logging with request IDs

Plain text logs cannot be queried. Emit one JSON object per line to stdout and let the platform ship it. Attach the request ID automatically from the context variable so every line from every layer correlates, without threading an ID through function signatures.

```python
import contextvars
import json
import logging
import sys

request_id_var = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    # The container log driver timestamps lines; add a "ts" field if yours does not.
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        payload.update(getattr(record, "ctx", {}))  # structured fields via extra={"ctx": {...}}
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), default=str)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
log = logging.getLogger("gateway")
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = False

token = request_id_var.set("req-7f3a")
log.info("chat completed", extra={"ctx": {"tenant": "acme", "model": "small", "tokens_in": 812, "latency_ms": 431}})
request_id_var.reset(token)
log.warning("outside a request")
```

Output:

```text
{"level":"INFO","logger":"gateway","msg":"chat completed","request_id":"req-7f3a","tenant":"acme","model":"small","tokens_in":812,"latency_ms":431}
{"level":"WARNING","logger":"gateway","msg":"outside a request","request_id":"-"}
```

Remember that `uvicorn` has its own loggers (`uvicorn.error`, `uvicorn.access`); configure them through `--log-config` or `logging.config.dictConfig` so their output uses the same formatter, and never log prompts, tokens or `Authorization` headers.

### OpenTelemetry tracing

Logs tell you what one request said; traces show where its time went across FastAPI, SQLAlchemy, Redis and the LLM provider. The instrumentation packages create spans automatically and propagate the W3C `traceparent` header on outgoing `httpx` calls so downstream services join the same trace.

```python
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine


def setup_tracing(app: FastAPI, engine: AsyncEngine, service_name: str, otlp_endpoint: str) -> None:
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))  # e.g. http://collector:4318/v1/traces
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


tracer = trace.get_tracer(__name__)


async def call_llm(model: str, prompt: str) -> str:
    with tracer.start_as_current_span("llm.completion") as span:
        span.set_attribute("llm.model", model)
        span.set_attribute("llm.prompt_chars", len(prompt))
        ...  # the provider call; httpx instrumentation adds a child span
        return "answer"
```

Three production details: initialise the SDK inside each worker process (after fork), because the batch exporter's background thread does not survive `fork()`; sample in production (`ParentBased` with a ratio) instead of exporting everything; and add the trace ID to your JSON logs (`format(span.get_span_context().trace_id, "032x")`) so a log line leads straight to its trace. Instrument the `sync_engine` of an async SQLAlchemy engine.

### Health, readiness and background work

Kubernetes needs two different answers. **Liveness** (`/healthz`) says the process is not wedged and must not touch dependencies, or a database blip restarts every pod at once. **Readiness** (`/readyz`) says this instance can serve now: check the database with a short timeout and only dependencies the endpoint truly needs.

```python
import asyncio

from fastapi import FastAPI, Request, Response
from sqlalchemy import text

app = FastAPI()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(request: Request, response: Response) -> dict[str, str]:
    try:
        async with asyncio.timeout(1.0):  # Python 3.11+
            async with request.app.state.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
    except Exception:
        response.status_code = 503
        return {"status": "unavailable", "postgres": "down"}
    return {"status": "ready", "postgres": "ok"}
```

`BackgroundTasks` runs a function after the response is sent, inside the same worker process. That is fine for best-effort work such as cache warm-up or an audit log line. It is not a queue: there is no persistence, no retry, no visibility, no backpressure, and a restart or crash loses pending tasks. Anything that must happen (send the receipt, embed the uploaded document, charge the card) belongs in a durable queue: arq (asyncio and Redis), Celery or Dramatiq for richer needs, RQ for simplicity. Make jobs idempotent and pass identifiers, never request-scoped objects.

```python
from arq import create_pool
from arq.connections import RedisSettings


async def generate_embeddings(ctx: dict, document_id: str) -> int:
    ...  # load the document by id, chunk, embed, store; safe to run twice
    return 0


class WorkerSettings:  # run with: arq app.worker.WorkerSettings
    functions = [generate_embeddings]
    redis_settings = RedisSettings(host="redis")
    max_tries = 5
    job_timeout = 300


async def enqueue_embedding(document_id: str) -> None:
    redis = await create_pool(RedisSettings(host="redis"))  # in real code create once in lifespan
    await redis.enqueue_job("generate_embeddings", document_id, _job_id=f"embed:{document_id}")
```

The `_job_id` gives you deduplication: enqueueing the same ID twice while the first exists is a no-op, which pairs with idempotent handlers to survive retries.

### Workers, graceful shutdown and containers

Each uvicorn worker is a separate process with its own event loop, connection pools and memory. `uvicorn app.main:app --workers 4` supervises them simply; gunicorn with the `uvicorn-worker` package (`uvicorn_worker.UvicornWorker`; the older `uvicorn.workers` module is deprecated) adds mature process management such as max-requests recycling. On Kubernetes the common advice is one process per container with several replicas, because the orchestrator already restarts and scales pods and CPU limits stay meaningful. Multiple workers earn their place on a VM or when per-process memory is small.

```bash
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 25 --proxy-headers --forwarded-allow-ips="10.0.0.0/8"

gunicorn app.main:app -k uvicorn_worker.UvicornWorker -w 4 --graceful-timeout 30 --timeout 60 --max-requests 10000 --max-requests-jitter 500
```

On `SIGTERM` uvicorn stops accepting connections, waits for in-flight requests, runs lifespan shutdown (closing pools and clients), then exits; `--timeout-graceful-shutdown` caps the wait. Your orchestrator's `terminationGracePeriodSeconds` must exceed that cap, and a short `preStop` sleep covers the delay before the load balancer stops sending traffic. The logic is easy to model:

```python
import asyncio


class Drainer:
    """Tracks in-flight work; once draining, new work is refused (503) and shutdown waits for the rest."""

    def __init__(self) -> None:
        self.draining = False
        self._inflight = 0
        self._idle = asyncio.Event()
        self._idle.set()

    async def handle(self, name: str, seconds: float) -> str:
        if self.draining:
            return f"{name}: 503 shutting down"
        self._inflight += 1
        self._idle.clear()
        try:
            await asyncio.sleep(seconds)
            return f"{name}: 200"
        finally:
            self._inflight -= 1
            if self._inflight == 0:
                self._idle.set()

    async def shutdown(self, timeout: float) -> bool:
        self.draining = True
        try:
            await asyncio.wait_for(self._idle.wait(), timeout)
            return True
        except TimeoutError:
            return False


async def scenario(timeout: float) -> None:
    d = Drainer()
    slow = asyncio.create_task(d.handle("llm-call", 0.2))
    await asyncio.sleep(0.05)
    clean = await d.shutdown(timeout)
    late = await d.handle("late-request", 0.0)
    print(f"timeout={timeout}: drained_cleanly={clean}; {late}")
    if slow.done():
        print(slow.result())
    else:
        slow.cancel()
        print("llm-call: cancelled")
        await asyncio.gather(slow, return_exceptions=True)


asyncio.run(scenario(1.0))
asyncio.run(scenario(0.05))
```

Output:

```text
timeout=1.0: drained_cleanly=True; late-request: 503 shutting down
llm-call: 200
timeout=0.05: drained_cleanly=False; late-request: 503 shutting down
llm-call: cancelled
```

A long LLM call that outlives the grace period is cut off, which is why slow work belongs in a queue or must be resumable. The container image should be small, run as a non-root user, and use exec-form `CMD` so the server is PID 1 and receives `SIGTERM` directly:

```text
FROM python:3.12-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN useradd --create-home --uid 10001 app
COPY --from=build /install /usr/local
WORKDIR /app
COPY --chown=app:app app ./app
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "25"]
```

Configuration differs by environment but code should not branch on environment names scattered through modules. Read one `Settings` object (pydantic-settings, as in the dependency-injection lesson) and derive behaviour in the app factory: in production disable the interactive docs (`FastAPI(docs_url=None, redoc_url=None, openapi_url=None)`), enable sampling and JSON logs, and require secrets to be present at boot so a misconfigured pod fails readiness instead of failing requests.

> **Production note:** Run migrations as a separate pre-deploy job, set CPU and memory limits, and alert on the saturation signals (event loop lag, pool wait time, queue depth) rather than only on error rate.

## Practical Backend Scenario

Your document-ingestion API accepts a PDF, extracts text, embeds chunks and answers questions with an LLM. After a Friday deploy, customers report missing documents: uploads returned `202` but never became searchable. Investigation shows embedding ran in `BackgroundTasks`, and the rolling restart killed pods with tasks pending. The fix is to enqueue an idempotent `generate_embeddings` job in arq keyed by document ID, return `202` with a status URL, set `--timeout-graceful-shutdown` and the pod grace period consistently, add `/readyz`, and log the request ID and job ID on every line so a single customer complaint can be traced from upload through the worker to the LLM call.

## Practice Loop

1. Add the pure ASGI request-ID middleware to a FastAPI app and prove, with a test, that the inbound header is echoed and that a generated one appears when absent.
2. Install problem+json handlers for domain errors, validation errors and `HTTPException`, then write one test per envelope.
3. Configure a JSON log formatter for your app and for `uvicorn.access`, hit an endpoint, and confirm the request ID appears in every line.
4. Wire OpenTelemetry with a console exporter, create a manual span around a fake LLM call, and print the trace ID inside a log line.
5. Implement `/healthz` and `/readyz`, stop your database container, and verify only readiness fails.
6. Move a `BackgroundTasks` job to a queue (arq or RQ), kill the worker mid-job, restart it and confirm the job is retried.
7. Build the Docker image, run it as non-root, send `SIGTERM` during a slow request with `docker stop`, and measure how long the request is allowed to finish.

## Evidence of Understanding

- I can justify, for a given concern, whether it belongs in middleware or a dependency.
- I can explain why `BaseHTTPMiddleware` is avoided on hot paths and write a pure ASGI alternative.
- I can produce an RFC 9457 error body and explain how unhandled exceptions flow through Starlette.
- I can show how a request ID reaches every log line without being passed as an argument.
- I can describe what liveness and readiness each check and the failure each prevents.
- I can state exactly what is lost when a worker restarts with `BackgroundTasks` pending, and how a queue changes that.
- I can relate the grace period chain: uvicorn timeout, orchestrator grace period, load balancer deregistration.

## Interview Questions to Rehearse

### Q: When would you use middleware instead of a dependency?
For concerns that apply to every request regardless of route, including 404s and errors, and that operate on raw ASGI messages: request IDs, timing, security headers. Anything needing typed request data, per-route behaviour or test overrides (auth, tenant, pagination) is a dependency.

### Q: Why avoid BaseHTTPMiddleware?
It runs the downstream app in a separate task and wraps the response body, which breaks context variable propagation back to the middleware, complicates streaming and cancellation, and adds overhead. A pure ASGI middleware is a few more lines but has no such surprises.

### Q: How do you correlate logs, traces and requests?
Generate or accept a request ID at the edge, store it in a context variable, inject it in the JSON formatter, return it in a response header, and include the OpenTelemetry trace ID in logs. Then a customer-visible ID leads to both log lines and the full trace.

### Q: BackgroundTasks or Celery?
BackgroundTasks for cheap, best-effort follow-ups where loss is acceptable. A queue when work must survive restarts, needs retries with backoff, rate control, visibility or runs longer than the shutdown grace period. In both cases the work should be idempotent and take IDs, not objects.

### Q: What happens to in-flight requests during a deploy?
The orchestrator sends SIGTERM and removes the pod from endpoints concurrently. The server stops accepting new connections, finishes in-flight requests up to the graceful timeout, runs lifespan shutdown, and exits. If the grace period is shorter than the slowest legitimate request, those requests are killed, so align the timeouts and move long work to a queue.

### Q: How many workers should a FastAPI container run?
On Kubernetes usually one per container and scale replicas, which keeps limits, restarts and metrics simple. On a single VM, roughly one per core, remembering that each worker has its own memory (model weights) and its own database pool, so multiply pool sizes accordingly.

## Common Pitfalls

- **Liveness probe hitting the database:** a transient outage restarts every pod and turns an incident into an outage.
- **Shell-form `CMD` in Docker:** a shell becomes PID 1, `SIGTERM` never reaches the server, and every deploy ends in a hard kill after the grace period.
- **Initialising tracing or engines before `fork`:** background exporter threads and connection pools do not survive forking. Initialise per worker.
- **Logging raw prompts and headers:** leaks customer data and credentials. Log sizes, IDs and hashes.
- **Per-process state assumed global:** in-memory caches, rate limits and counters are per worker. Use Redis or the database for shared state.
- **Unbounded concurrency to the LLM provider:** one slow provider exhausts the event loop's tasks and your pool. Use timeouts, a semaphore and a circuit breaker.
- **Interactive docs exposed in production:** it advertises your whole API surface. Disable it or protect it.
- **Treating 500s as the only metric:** latency, saturation and queue depth warn you before errors do.

## Suggested Extension

Add a `/metrics` endpoint with Prometheus counters and histograms (requests by route and status, LLM latency by model, queue depth), then write an alert rule for p95 latency and for a queue backlog older than five minutes. Finish with a load test that sends `SIGTERM` mid-test and asserts that no request fails.
