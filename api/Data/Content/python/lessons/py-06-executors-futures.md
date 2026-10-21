# Executors and Futures

Raw `threading.Thread` objects have no return value, no error channel and no cap on how many you create. `concurrent.futures` fixes all three with one abstraction: submit a callable, get a handle back, and let a bounded pool do the scheduling. In production this is the layer that stops an LLM gateway from opening 5,000 sockets, and in an interview it is where "what happens when one task raises?" and "why did my process pool hang?" separate seniors from people who memorised the API.

## Concepts Covered

### Executors: a pool plus a queue

An `Executor` owns a set of workers and a **work queue**. `submit(fn, *args, **kwargs)` enqueues a call and returns a `Future` immediately. `ThreadPoolExecutor` runs calls in threads of the current process, so it suits I/O-bound work (HTTP, database drivers, file reads) where the GIL is released while waiting. `ProcessPoolExecutor` runs calls in separate interpreters, each with its own GIL, so it suits CPU-bound work such as parsing, tokenising or image transforms.

Defaults worth knowing: `ThreadPoolExecutor` uses `min(32, os.cpu_count() + 4)` workers (3.8+), `ProcessPoolExecutor` uses `os.cpu_count()`. Leaving the `with` block calls `shutdown(wait=True)`, which blocks until every queued and running task is finished. That is why code that prints `future.done()` after the `with` block always sees `True`, while code that prints it inside the block right after `submit` usually sees `False`.

On a free-threaded build (3.13t and later) threads can run Python bytecode in parallel, which narrows the gap between the two executors for CPU work. Do not rely on it for portable code yet. Python 3.14 also adds `InterpreterPoolExecutor`, which runs each worker in its own subinterpreter.

### Futures: a small state machine that carries exceptions

A `Future` moves through `PENDING`, `RUNNING` and then `FINISHED` or `CANCELLED`. The worker stores either the return value or the exception on the future. Nothing is raised in the worker thread's context and nothing is raised in the submitting thread until you ask:

- `done()` never blocks and never raises. It only reports status.
- `result(timeout=None)` blocks, then returns the value or **re-raises the stored exception** (with its original traceback). It raises `CancelledError` for a cancelled future and `TimeoutError` if the timeout expires. In 3.11+ `concurrent.futures.TimeoutError` is the builtin `TimeoutError`.
- `exception(timeout=None)` blocks and returns the exception instead of raising it, or `None`.
- `add_done_callback(fn)` calls `fn(future)` in whichever thread completes the future, or immediately in the caller if it is already done. Exceptions inside callbacks are logged and swallowed, so callbacks are for bookkeeping, not for control flow.

Contrast this with a raw `Thread`: an exception in `target` prints a traceback through `threading.excepthook` and the thread dies. The parent never learns about it unless you build your own channel. A future is that channel.

```python
import time
from concurrent.futures import CancelledError, ThreadPoolExecutor

def slow(tag: str, seconds: float) -> str:
    time.sleep(seconds)
    return tag

pool = ThreadPoolExecutor(max_workers=1)
running = pool.submit(slow, "running", 0.3)
queued = pool.submit(slow, "queued", 0.1)
time.sleep(0.05)
print("running.cancel() ->", running.cancel())   # already executing
print("queued.cancel()  ->", queued.cancel())    # still in the queue
try:
    queued.result()
except CancelledError:
    print("queued.result() raised CancelledError")
pool.shutdown(wait=True, cancel_futures=True)
print("final:", running.result())
```

```text
running.cancel() -> False
queued.cancel()  -> True
queued.result() raised CancelledError
final: running
```

`cancel()` only succeeds while the future is pending. A running task cannot be interrupted by the executor, because Python has no safe way to kill a thread. Real cancellation requires cooperation: a `threading.Event` the task polls, or a socket timeout.

### map versus submit plus as_completed

`executor.map(fn, iterable)` is a lazy generator of results **in input order**, not completion order. If the slowest task is first, every later result waits behind it. If a task raises, the exception surfaces **when iteration reaches that item**, the generator is finished, and the remaining pending futures are cancelled. You lose the results you had not yet consumed.

`submit` plus `as_completed` yields futures in completion order and lets you handle each failure independently, at the cost of a bookkeeping dict mapping futures back to inputs.

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def embed(doc_id: int) -> list[float]:
    time.sleep(0.05 * (4 - doc_id))
    if doc_id == 2:
        raise ConnectionError(f"provider reset on doc {doc_id}")
    return [float(doc_id)]

with ThreadPoolExecutor(max_workers=4) as pool:
    futs = {pool.submit(embed, i): i for i in range(4)}
    for fut in as_completed(futs):
        doc = futs[fut]
        try:
            print(f"doc {doc} ok {fut.result()}")
        except ConnectionError as exc:
            print(f"doc {doc} failed: {exc}")

with ThreadPoolExecutor(max_workers=4) as pool:
    try:
        for vec in pool.map(embed, range(4)):
            print("got", vec)
    except ConnectionError as exc:
        print("map stopped:", exc)
```

```text
doc 3 ok [3.0]
doc 2 failed: provider reset on doc 2
doc 1 ok [1.0]
doc 0 ok [0.0]
got [0.0]
got [1.0]
map stopped: provider reset on doc 2
```

Use `map` when every item must succeed and you want ordered output with minimal code. Use `as_completed` when partial success is acceptable, when you want to stream results to the user as they arrive, or when you need per-task retry. `wait(futures, timeout=..., return_when=FIRST_COMPLETED | FIRST_EXCEPTION | ALL_COMPLETED)` is the third tool: it returns `(done, not_done)` sets and is the right primitive for "fail the batch on the first error" or for hedged requests. Note that `map(..., timeout=)` and `as_completed(..., timeout=)` apply to the **whole** iteration, not per task.

### Shutdown and cancellation semantics

`shutdown(wait=True, cancel_futures=True)` (3.9+) cancels every pending future and then waits for running ones. Since 3.9 worker threads are non-daemon and are joined at interpreter exit, so one hung HTTP call with no timeout will keep your process alive after `main` returns. The fix is always a timeout on the blocking call itself, because the executor cannot reach inside it.

### ProcessPoolExecutor: pickling, start methods and broken pools

Arguments, return values and the callable itself cross a process boundary via `pickle`. Consequences:

- The callable must be importable at module top level. Lambdas fail with `PicklingError`, and nested functions or closures fail with `PicklingError` or `AttributeError: Can't pickle local object` depending on the version. Either way the error appears on `future.result()`, not at `submit`.
- Arguments and results must be picklable and small. Sending a 500 MB DataFrame to a worker costs more than computing on it. Pass file paths or shared-memory handles instead.
- Use `chunksize` with `map` (it only affects `ProcessPoolExecutor`) so thousands of tiny items are batched into fewer IPC round trips.
- Guard entry points with `if __name__ == "__main__":`. With `spawn` (the default on Windows and macOS), each worker re-imports your main module, and an unguarded pool creation recurses.
- The default start method on Linux was `fork` through 3.13 and becomes `forkserver` in 3.14. `fork` after threads exist can deadlock on inherited locks, so pass an explicit `mp_context=multiprocessing.get_context("spawn")` in services that use threads.
- If a worker dies (segfault, OOM kill, `os._exit`), the pool becomes broken and every pending future fails with `BrokenProcessPool`. Treat it as a restart-the-pool event. `max_tasks_per_child` (3.11+) recycles workers to contain memory leaks in native libraries.

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

def tokenize_stats(doc: str) -> tuple[int, int]:
    words = doc.split()
    return len(words), len(set(words))

if __name__ == "__main__":
    docs = ["a b a", "x y z x", "hello"]
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as pool:
        print(list(pool.map(tokenize_stats, docs, chunksize=2)))
```

```text
[(3, 2), (4, 3), (1, 1)]
```

> **Pitfall:** `pool.submit(lambda c: sum(c), [1, 2])` on a `ProcessPoolExecutor` does not fail when you submit it. It fails later, with `PicklingError`, when you call `result()`.

### Backpressure and pool starvation

Both executors use an **unbounded** internal queue. Submitting 10 million items from a fast producer just stores 10 million work items in memory. A bounded semaphore around `submit` gives you backpressure:

```python
import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor

class BoundedExecutor:
    """submit() blocks once max_pending tasks are queued or running."""

    def __init__(self, max_workers: int, max_pending: int) -> None:
        self._pool = ThreadPoolExecutor(max_workers=max_workers)
        self._slots = threading.BoundedSemaphore(max_pending)

    def submit[**P, T](self, fn: Callable[P, T], /, *args: P.args, **kwargs: P.kwargs) -> Future[T]:
        self._slots.acquire()
        try:
            fut = self._pool.submit(fn, *args, **kwargs)
        except BaseException:
            self._slots.release()
            raise
        fut.add_done_callback(lambda _: self._slots.release())
        return fut

    def shutdown(self) -> None:
        self._pool.shutdown(wait=True)
```

A related trap is **pool starvation**: a task running on the pool submits a child task to the same pool and waits for it. With `max_workers=1` (or any pool where every worker is a waiting parent) the child never starts.

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError

pool = ThreadPoolExecutor(max_workers=1)

def child() -> str:
    return "child"

def parent() -> str:
    return pool.submit(child).result(timeout=1)   # without the timeout this hangs forever

try:
    print(pool.submit(parent).result())
except TimeoutError:
    print("pool starved: parent waits for a child that can never start")
pool.shutdown()
```

The rule: never block a pool worker on work that needs the same pool. Use separate pools per stage, or restructure so the parent submits children and returns, with a coordinator collecting futures.

### Where this connects to asyncio

`loop.run_in_executor(pool, fn, *args)` and `asyncio.to_thread(fn, *args)` wrap exactly these executors so that blocking calls do not freeze an event loop. Everything here (pickling limits, bounded queues, exceptions stored on futures) applies unchanged, which is why the next lesson's async introduction builds on it.

## Practical Backend Scenario

Your LLM gateway ingests uploaded PDFs. For each PDF it must call an embeddings provider for 200 chunks (I/O-bound, provider allows 16 concurrent requests) and, before that, run a CPU-heavy layout parser (pure Python plus a C extension that does not release the GIL). A single `ThreadPoolExecutor(max_workers=200)` hammers the provider into 429s and serialises the parser on one core. The robust design uses a `ProcessPoolExecutor` sized to cores for parsing, passing file paths rather than bytes, and a `BoundedExecutor` of 16 workers for embedding calls, with a timeout on every HTTP request. Results are gathered with `as_completed`, so one failed chunk is retried or recorded without discarding the other 199, and a `BrokenProcessPool` from a crashing parser triggers pool recreation and a dead-letter entry for the offending file.

## Practice Loop

1. Time a CPU-bound function (sum of squares up to 20 million) over 4 inputs with `ThreadPoolExecutor(4)`, `ProcessPoolExecutor(4)` and sequentially. Record the three timings and explain them.
2. Submit five tasks that sleep 0.1 s to `ThreadPoolExecutor(2)`. Log start and end timestamps to prove that at most two ran at once.
3. Make the third of ten tasks raise. Compare the behaviour of `map`, then `submit` with `result()` in submission order, then `as_completed`. Note which results you lose with each.
4. Pass a lambda to a `ProcessPoolExecutor`, observe where the error appears, then fix it with a top-level function. Add a `mp_context` of `spawn` and keep the `__main__` guard.
5. Reproduce pool starvation with `max_workers=1`, then fix it with a second pool and a timeout.
6. Implement `BoundedExecutor` from this lesson, then show that a producer submitting 1,000 items never has more than `max_pending` in flight.

## Evidence of Understanding

- I can state which executor to choose for a workload and justify it by naming the resource that is the bottleneck.
- I can predict the order and exception behaviour of `map`, `submit` with `result()`, and `as_completed` for a batch where one task fails.
- I can explain why `done()` never raises, why `with` makes `done()` true afterwards, and why `cancel()` fails on a running task.
- I can list three pickling-related failures in a process pool and fix each.
- I can explain why an executor queue is unbounded and add backpressure.
- I can diagnose a pool-starvation hang from a thread dump.

## Interview Questions to Rehearse

### Q: When would `map` be the wrong choice compared with `submit` plus `as_completed`?

When partial results matter. `map` returns results in input order and stops at the first exception, cancelling pending work, so one slow or failing early item blocks or discards everything behind it. `as_completed` yields in finish order and lets me catch each future's exception separately, which is what I want for fan-out calls to a flaky provider.

### Q: A teammate says "I used a ThreadPoolExecutor so my counter is thread-safe." What is wrong?

The executor only schedules calls and collects results. It adds no mutual exclusion. `counter += 1` is a read, add and write sequence that can interleave across threads, so I either protect it with a `Lock`, or better, have each task return its contribution and aggregate in the caller, which avoids shared mutable state.

### Q: Why does a `ProcessPoolExecutor` job fail with `PicklingError` only when you call `result()`?

`submit` returns a future after enqueuing. Pickling happens in a feeder thread when the call is sent to a worker, and the failure is stored on the future. Lambdas, closures and objects holding locks, sockets or generators cannot be pickled. The remedy is top-level functions and plain data arguments.

### Q: How do you cancel a running task in an executor?

You cannot, directly. `Future.cancel()` only works on pending futures. For running work I design cancellation in: an `Event` the loop checks, short I/O timeouts, or in a process pool a sentinel file or shared flag. `shutdown(cancel_futures=True)` drops the queue but still waits for running tasks.

### Q: Your service hangs on shutdown after `main` returned. Why?

Pool threads are non-daemon since 3.9 and joined at exit, so a task blocked on a network call with no timeout keeps the process alive. I add timeouts at the call site, call `shutdown(wait=False, cancel_futures=True)` in the signal handler, and make sure no worker waits on a task queued in its own pool.

### Q: What changes with free-threaded Python for executors?

Threads can run bytecode on multiple cores, so `ThreadPoolExecutor` can speed up CPU-bound pure Python without the pickling cost. But locking, thread-safety of shared data and extension-module compatibility become my responsibility, so I benchmark before dropping process pools.

## Common Pitfalls

- Treating `done()` as an error check. It only reports completion. Call `result()` or `exception()` to observe failures.
- Forgetting to consume `map`'s generator. Exceptions surface only on iteration, and an unconsumed `map` swallows them silently.
- Submitting fire-and-forget futures and discarding them. Exceptions then vanish; keep the futures or attach a done-callback that logs `fut.exception()`.
- Sizing a `ThreadPoolExecutor` at "as many as tasks". Respect downstream limits (rate limits, DB connection pools) rather than the task count.
- Creating a new pool per request. Pools are expensive; create once and share, or you pay thread/process start-up every time.
- Passing large objects to a process pool. Pickle cost can exceed compute cost.
- Using `fork` in a multi-threaded service. Prefer `spawn` or `forkserver`.
- Waiting on a child future from inside the same pool, which deadlocks when workers are exhausted.

## Suggested Extension

Build a `run_hedged(fn, replicas, delay)` helper: start the first call, and if it has not finished after `delay` seconds start a second, return the first successful result with `wait(..., return_when=FIRST_COMPLETED)`, and cancel the loser if it is still pending. Handle the case where the first finisher failed and the other may still succeed.
