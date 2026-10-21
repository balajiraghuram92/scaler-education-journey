# Async Patterns, Backpressure and Blocking Calls

Most async services fail in production not because of exotic bugs but because nothing limits them: 50,000 tasks hit one embedding API, an unbounded queue eats the heap while a slow consumer falls behind, a single blocking SDK call freezes every request, or a request ID vanishes from the logs the moment work moves to a thread. This lesson covers the patterns that keep an async service stable under load, and the diagnostics interviewers expect you to reach for when someone says "the service is slow but CPU is low".

## Concepts Covered

### Semaphore-bounded fan-out

A semaphore caps how many coroutines are *inside* a section at once. It is the simplest way to stop a fan-out from overwhelming a dependency.

```python
import asyncio

async def embed_all(chunks: list[str], limit: int) -> tuple[list[int], int]:
    sem = asyncio.Semaphore(limit)
    in_flight = peak = 0

    async def embed(chunk: str) -> int:
        nonlocal in_flight, peak
        async with sem:                      # at most `limit` bodies run at once
            in_flight += 1
            peak = max(peak, in_flight)
            await asyncio.sleep(0.01)        # stands in for an HTTP call
            in_flight -= 1
            return len(chunk)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(embed(c)) for c in chunks]
    return [t.result() for t in tasks], peak

lengths, peak = asyncio.run(embed_all(["x" * n for n in range(1, 41)], limit=5))
print(len(lengths), "chunks, peak concurrency =", peak)
```

```text
40 chunks, peak concurrency = 5
```

The limit is on concurrency, not on tasks: this code still creates one task and one coroutine frame per chunk up front. For 40 items that is irrelevant; for 5 million lines of a file it is a memory problem. When the input is large or unbounded, use a fixed worker pool fed by a bounded queue instead. Also keep the semaphore limit at or below the connection pool size of the client it protects, otherwise tasks pass the semaphore and then wait on the pool.

### Producer/consumer with asyncio.Queue

A queue decouples production from consumption, and `maxsize` is what turns it into backpressure: `await queue.put(x)` suspends the producer when the queue is full, so a slow consumer slows the producer instead of growing memory. An unbounded `asyncio.Queue()` (the default, `maxsize=0`) has no backpressure at all.

```python
import asyncio

async def consumer(name: str, queue: asyncio.Queue[str | None], done: list[str]) -> None:
    while True:
        item = await queue.get()
        try:
            if item is None:                  # sentinel: this consumer is told to stop
                return
            await asyncio.sleep(0.01)         # slow downstream (an embedding API, say)
            done.append(item)
        finally:
            queue.task_done()                 # always, or join() can hang forever

async def main() -> None:
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=2)
    done: list[str] = []
    peak = 0
    async with asyncio.TaskGroup() as tg:
        for i in range(3):
            tg.create_task(consumer(f"w{i}", queue, done))
        for n in range(10):
            await queue.put(f"doc-{n}")       # suspends while the queue is full
            peak = max(peak, queue.qsize())
        for _ in range(3):
            await queue.put(None)             # exactly one sentinel per consumer
        await queue.join()
    print(f"processed={len(done)} peak queue size={peak}")

asyncio.run(main())
```

```text
processed=10 peak queue size=2
```

Graceful shutdown has three rules. First, send one stop signal per consumer; with three consumers and one sentinel, one stops and two wait forever. Second, call `task_done()` for every `get()`, including on error paths, because `join()` returns only when the unfinished counter reaches zero. Third, decide what a shutdown means: drain what is queued, or drop it.

Python 3.13 added `Queue.shutdown()`, which removes the need for sentinels. After `shutdown()`, `put` raises `asyncio.QueueShutDown`, and `get` keeps returning queued items until the queue is empty, then raises `QueueShutDown`, which consumers catch to exit. `shutdown(immediate=True)` discards queued items instead of draining them. I ran this on 3.13; if you must support 3.12, use sentinels.

> **Interview tip:** `asyncio.Queue` is not thread-safe. From a worker thread, hand items to the loop with `loop.call_soon_threadsafe(queue.put_nowait, item)` or `asyncio.run_coroutine_threadsafe(queue.put(item), loop)`.

### Reusing httpx.AsyncClient and its connection pool

An `httpx.AsyncClient` owns a connection pool with keep-alive. Creating one per request throws away that pool, so every call pays DNS, TCP and TLS setup again, and under load you leak sockets in `TIME_WAIT`. Create one client per upstream at application start-up, share it, and close it at shutdown.

```python
import httpx

limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)
timeout = httpx.Timeout(10.0, connect=2.0, pool=1.0)

async def embed_batch(client: httpx.AsyncClient, texts: list[str]) -> list[list[float]]:
    resp = await client.post("/v1/embeddings", json={"input": texts})
    resp.raise_for_status()
    return [row["embedding"] for row in resp.json()["data"]]

async def run(batches: list[list[str]]) -> None:
    async with httpx.AsyncClient(
        base_url="https://api.example.com", limits=limits, timeout=timeout
    ) as client:
        for batch in batches:
            await embed_batch(client, batch)
```

Know what each knob does: `max_connections` caps simultaneous sockets, `max_keepalive_connections` caps idle ones kept for reuse, and the `pool` timeout is how long a request waits for a free connection before `httpx.PoolTimeout`. httpx's default timeout is 5 seconds, which is rarely right for LLM calls: set connect short and read long. In FastAPI the shared client belongs in the lifespan handler and on `app.state`; the next lessons build that wiring.

### Detecting blocking calls

Symptoms: latency spikes across unrelated endpoints, health checks timing out, CPU at 100% of one core. Three tools find the cause.

Debug mode (`asyncio.run(main(), debug=True)`, `python -X dev`, or `PYTHONASYNCIODEBUG=1`) logs any callback or task step that holds the loop longer than `loop.slow_callback_duration` (default 0.1 s):

```python
import asyncio, logging, time
logging.basicConfig(level=logging.WARNING, format="%(name)s %(levelname)s %(message)s")

async def parse_big_payload() -> None:
    time.sleep(0.25)          # stands in for json.loads on 80 MB or a sync SDK call

async def main() -> None:
    await parse_big_payload()

asyncio.run(main(), debug=True)
```

```text
asyncio WARNING Executing <Task finished name='Task-1' coro=<main() done, defined at <stdin>:7> result=None created at ...> took 0.254 seconds
```

Debug mode is slow, so you do not leave it on in production. There, run a **loop-lag monitor**: a task that sleeps a short interval and records how late it woke up. The lag is exactly how long other work held the loop.

```python
import asyncio, time

async def loop_lag_monitor(interval: float, samples: list[float], stop: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    while not stop.is_set():
        expected = loop.time() + interval
        await asyncio.sleep(interval)
        samples.append(max(0.0, loop.time() - expected))   # how late the loop woke us

async def main() -> None:
    samples: list[float] = []
    stop = asyncio.Event()
    mon = asyncio.create_task(loop_lag_monitor(0.02, samples, stop))
    await asyncio.sleep(0.1)
    time.sleep(0.3)                 # the blocking call
    await asyncio.sleep(0.1)
    stop.set(); await mon
    print(f"worst lag >= 0.25s: {max(samples) >= 0.25}")

asyncio.run(main())
```

```text
worst lag >= 0.25s: True
```

Export that lag as a metric and alert on it. The third tool is a sampling profiler such as py-spy, which shows the blocking frame without code changes.

### to_thread, run_in_executor and the GIL

Blocking I/O (a sync SDK, file reads, a database driver without an async mode) belongs in a thread: `await asyncio.to_thread(func, *args)`. It runs on the loop's default `ThreadPoolExecutor`, whose size is `min(32, os.cpu_count() + 4)`, so a flood of blocking calls queues behind that limit; size it with `loop.set_default_executor(...)` or use your own executor through `loop.run_in_executor(executor, func, *args)`.

Threads do not make CPU-bound pure-Python work faster, because of the GIL. They keep the loop responsive, but two CPU-bound threads still take turns. For CPU-bound work (tokenising large documents, parsing) use a `ProcessPoolExecutor` through `run_in_executor`, remembering that arguments and results must be picklable. On a free-threaded 3.13t build threads can run Python code in parallel, but treat that as experimental.

One detail interviewers love: `to_thread` copies the current `contextvars` context into the worker thread, but `run_in_executor` does not.

```python
import asyncio, contextvars
rid = contextvars.ContextVar("rid", default="-")
def read(): return rid.get()

async def main():
    rid.set("req-9")
    loop = asyncio.get_running_loop()
    print("to_thread:       ", await asyncio.to_thread(read))
    print("run_in_executor: ", await loop.run_in_executor(None, read))
    ctx = contextvars.copy_context()
    print("with copy_context:", await loop.run_in_executor(None, ctx.run, read))

asyncio.run(main())
```

```text
to_thread:        req-9
run_in_executor:  -
with copy_context: req-9
```

### contextvars for request IDs

A `ContextVar` gives each logical flow its own value without passing it through every function. Every task gets a *copy* of the context at creation, so concurrent requests do not see each other's values, and a `set` inside a child task does not leak to the parent. Note the asymmetry: awaiting a plain coroutine runs in the caller's context, so its `set` is visible afterwards.

```python
import asyncio, contextvars, logging, time

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True

handler = logging.StreamHandler()
handler.addFilter(RequestIdFilter())
handler.setFormatter(logging.Formatter("[%(request_id)s] %(threadName)s %(message)s"))
log = logging.getLogger("gw")
log.addHandler(handler); log.setLevel(logging.INFO); log.propagate = False

def blocking_tokenize(text: str) -> int:
    log.info("tokenizing in a worker thread")
    time.sleep(0.05)
    return len(text.split())

async def handle(req_id: str, text: str) -> int:
    request_id.set(req_id)
    log.info("start")
    n = await asyncio.to_thread(blocking_tokenize, text)   # context copied to the thread
    log.info("done %d tokens", n)
    return n

async def main() -> None:
    await asyncio.gather(handle("req-1", "a b c"), handle("req-2", "d e"))
    print("parent sees:", request_id.get())

asyncio.run(main())
```

```text
[req-1] MainThread start
[req-1] asyncio_0 tokenizing in a worker thread
[req-2] MainThread start
[req-2] asyncio_1 tokenizing in a worker thread
[req-1] MainThread done 3 tokens
[req-2] MainThread done 2 tokens
parent sees: -
```

`gather` wrapped each coroutine in its own task, which is why the two requests stay isolated. Middleware sets the ID once per request, and every log line, including those from threads started with `to_thread`, carries it.

### Rate limiting

A semaphore limits concurrency; a provider quota limits *rate*. With 20 ms calls and `Semaphore(10)` you can issue about 500 requests per second, far beyond a 50 requests per second quota, and the provider answers 429. A token bucket allows `rate` operations per second on average with bursts up to `burst`:

```python
import asyncio
import time
from collections.abc import Awaitable, Callable

_EPS = 1e-9   # float slack: after sleeping exactly long enough, the refill can fall a hair short


class TokenBucket:
    """Allows `rate` operations per second on average, with bursts of up to `burst`."""

    def __init__(
        self,
        rate: float,
        burst: int,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if rate <= 0 or burst < 1:
            raise ValueError("rate must be > 0 and burst >= 1")
        self._rate, self._burst = rate, burst
        self._clock, self._sleep = clock, sleep
        self._tokens = float(burst)
        self._updated = clock()
        self._lock = asyncio.Lock()        # asyncio.Lock wakes waiters in FIFO order

    def _refill(self) -> None:
        now = self._clock()
        self._tokens = min(float(self._burst), self._tokens + (now - self._updated) * self._rate)
        self._updated = now

    async def acquire(self, cost: float = 1.0) -> None:
        if cost <= 0 or cost > self._burst:
            raise ValueError("cost must be in (0, burst]")
        async with self._lock:
            while True:
                self._refill()
                if self._tokens >= cost - _EPS:
                    self._tokens = max(0.0, self._tokens - cost)
                    return
                await self._sleep((cost - self._tokens) / self._rate)
```

Injecting `clock` and `sleep` makes the limiter testable without real waiting. For LLM APIs the cost is often tokens, not requests: `acquire(cost=estimated_tokens)` works, provided the cost never exceeds `burst`. This limiter is per process; with several replicas you need a shared limiter (Redis) or a per-replica share of the quota.

## Practical Backend Scenario

You are loading a 200,000-document corpus into a vector store through an embedding API that allows 100 requests per second and 8 concurrent connections. The pipeline must not read the whole corpus into memory, must not exceed the quota, and must stop cleanly on failure. The design: a bounded queue (backpressure), a fixed set of workers (concurrency cap), a token bucket (rate cap), all inside a `TaskGroup` (failure and cancellation).

```python
import asyncio
from collections.abc import Awaitable, Callable

async def ingest(
    docs: list[str],
    embed: Callable[[str], Awaitable[list[float]]],
    *,
    workers: int,
    bucket: TokenBucket,
) -> dict[str, list[float]]:
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=workers * 2)   # backpressure
    vectors: dict[str, list[float]] = {}

    async def worker() -> None:
        while (doc := await queue.get()) is not None:
            await bucket.acquire()               # provider quota: requests per second
            vectors[doc] = await embed(doc)      # concurrency is capped by `workers`

    async with asyncio.TaskGroup() as tg:
        for _ in range(workers):
            tg.create_task(worker())
        for doc in docs:
            await queue.put(doc)
        for _ in range(workers):
            await queue.put(None)
    return vectors
```

I ran it with 60 documents, a fake 20 ms embedder, 8 workers and `TokenBucket(100, 10)`: all 60 were embedded, peak in-flight calls stayed at or below 8, and the run took at least 0.49 s, which is what a 100 per second quota with a burst of 10 requires. If a worker raises, the `TaskGroup` cancels the other workers and the producer, which is blocked on `put`, so nothing deadlocks. In the real service the `embed` callable would use the shared `httpx.AsyncClient` from earlier, with the pool limit matching the worker count.

## Practice Loop

1. Run the semaphore example with `limit=1`, `5` and `40` and watch peak concurrency. Then replace the `TaskGroup` with 100,000 chunks and measure memory, and note why a worker pool is better.
2. Break the consumer by removing `task_done()` from the `finally`, then raise an exception for one item, and observe `join()` hang. Restore it.
3. Send only one sentinel to three consumers and see which ones never exit.
4. Insert `time.sleep(0.3)` in a handler and find it with `asyncio.run(..., debug=True)`, then with the lag monitor.
5. Compare `to_thread` and `run_in_executor` for a function that reads a `ContextVar`.
6. Run the `TokenBucket` with a fake clock and assert exact sleep durations.
7. Complete the two coding assignments below.

## Evidence of Understanding

- I can explain why a semaphore bounds concurrency but not task count, and when to use a worker pool instead.
- I can size a queue and explain what `put` does when it is full, and why unbounded queues hide overload.
- I can list the three rules of graceful consumer shutdown and describe `Queue.shutdown()` on 3.13.
- I can justify one shared `AsyncClient` per upstream and name the pool and timeout settings that matter.
- I can find a blocking call using debug mode, a loop-lag metric, or a profiler.
- I can choose between `to_thread`, a custom executor and a process pool, and say what the GIL changes.
- I can explain how a `ContextVar` propagates through tasks and `to_thread`, and why `run_in_executor` differs.
- I can distinguish a concurrency limit from a rate limit and implement the latter.

## Interview Questions to Rehearse

### Q: How does backpressure work with `asyncio.Queue`?
With a positive `maxsize`, `await queue.put()` suspends when the queue is full, so the producer cannot outrun the consumers. Memory is bounded and the slowness propagates upstream, for example to a reader that stops pulling from a file or socket. The default queue is unbounded and applies no backpressure, so overload shows up as memory growth instead.

### Q: A consumer pool hangs on shutdown. What do you check?
Whether every `get()` is matched by `task_done()` (including error paths), whether there is one sentinel per consumer, and whether the producer is blocked on a full queue while consumers are gone. On 3.13, `Queue.shutdown()` makes consumers exit through `QueueShutDown` once the queue drains.

### Q: Why create one `httpx.AsyncClient` instead of one per request?
The client holds the connection pool and keep-alive state, so reuse avoids repeated DNS, TCP and TLS setup and bounds open sockets with `Limits`. Per-request clients add latency and exhaust file descriptors under load. Create it in the app lifespan, set explicit timeouts, and close it on shutdown.

### Q: The service is slow but CPU is low and p99 is high across unrelated endpoints. How do you debug?
Suspect blocking the loop, or exhausted pools. Run debug mode in a test environment to see slow callbacks, check a loop-lag metric in production, and sample with py-spy. Then move the offending call to `to_thread` or a process pool, or replace it with an async client. Also check whether threads or the HTTP pool are saturated and requests are queueing.

### Q: `to_thread` versus `run_in_executor`: what differs?
`to_thread` uses the default thread pool and copies the current context into the thread, so `ContextVar`s such as request IDs survive. `run_in_executor` accepts any executor, including a process pool, and does not copy context unless you wrap the call with `ctx.run`. Neither bypasses the GIL for CPU-bound Python.

### Q: How do you enforce a provider rate limit in-process?
A token bucket gives a sustained rate with a bounded burst, usually combined with a concurrency cap. Inject the clock and sleep for tests, keep acquisition FIFO so waiters are not starved, and note that multiple replicas need a shared limiter or a quota split.

## Common Pitfalls

- Using a semaphore as a rate limiter; it caps concurrency, not requests per second.
- Unbounded queues, which turn a slow consumer into an out-of-memory crash.
- Forgetting `task_done()` on an error path, so `join()` never returns.
- Sending fewer sentinels than consumers, leaving some of them waiting forever.
- Creating an `AsyncClient` inside a handler, or leaving the default timeout on a long LLM call.
- Setting a semaphore larger than the client's `max_connections` and getting `PoolTimeout`.
- Calling sync SDKs or `json.loads` on huge payloads inside `async def`; CPU looks low overall but one core is pinned and every request stalls.
- Using `run_in_executor` and wondering why the request ID is missing from log lines written in the worker.
- Using threads for CPU-bound Python and expecting a speed-up.
- Setting a `ContextVar` in a plain awaited coroutine and being surprised it is visible to the caller afterwards.

## Suggested Extension

Extend the ingest pipeline with a retry layer: on HTTP 429 or a timeout, wait using exponential backoff with jitter, honour a `Retry-After` header by pausing the shared token bucket for all workers, and add a dead-letter list for items that fail after N attempts. Write tests with a fake clock that prove no worker issues a request during the pause.
