# asyncio in Depth

Almost every AI gateway, document pipeline and ride-hailing dispatcher you will be asked to design is an I/O fan-out problem, and asyncio is where Python handles it. The failures are rarely syntax errors: they are a task garbage-collected mid-flight, a cancellation swallowed by a broad `except`, a sibling call that keeps burning tokens after the request has failed, or one blocking call that freezes every other user. Interviewers probe exactly these seams, so this lesson goes below the `async`/`await` keywords into what the loop does and what the cancellation and error contracts really are.

## Concepts Covered

### What the event loop actually does

An event loop is one thread running a scheduler. It asks the OS selector which sockets are ready, moves ready callbacks onto a queue, and runs them one at a time. `await` is the only place a coroutine hands control back. Between two `await` points your code runs uninterrupted, so any blocking call or long CPU loop stalls every other task on that loop, including health checks and other users' requests.

```python
import asyncio, time

async def heartbeat(log: list[str]) -> None:
    for i in range(3):
        log.append(f"tick {i}")
        await asyncio.sleep(0.05)

async def bad_handler() -> None:
    time.sleep(0.3)           # blocks the loop thread

async def good_handler() -> None:
    await asyncio.sleep(0.3)  # yields to the loop

async def run(handler) -> list[str]:
    log: list[str] = []
    hb = asyncio.create_task(heartbeat(log))
    await asyncio.sleep(0)    # let the heartbeat start
    t0 = time.perf_counter()
    await handler()
    log.append(f"handler done after >= 0.3s: {time.perf_counter() - t0 >= 0.3}")
    await hb
    return log

print(asyncio.run(run(bad_handler)))
print(asyncio.run(run(good_handler)))
```

```text
['tick 0', 'handler done after >= 0.3s: True', 'tick 1', 'tick 2']
['tick 0', 'tick 1', 'tick 2', 'handler done after >= 0.3s: True']
```

The heartbeat could not tick while `time.sleep` held the thread. Concurrency here is cooperative: it exists only where you write `await`.

### Coroutine, Task and Future

These three are routinely confused in interviews.

- A **coroutine object** is what calling an `async def` function returns. Nothing has run yet; it is a suspended frame.
- A **Task** wraps a coroutine and schedules it on the loop, so it makes progress even if nobody is awaiting it yet.
- A **Future** is a low-level result slot with no code of its own, filled by a callback. `Task` is a subclass of `Future`; you rarely create bare futures outside library code.

```python
import asyncio

async def charge(order_id: str) -> str:
    print(f"  charge({order_id}) started")
    await asyncio.sleep(0)
    print(f"  charge({order_id}) finished")
    return f"paid:{order_id}"

async def main() -> None:
    coro = charge("A")                          # nothing runs
    print("created coroutine:", type(coro).__name__)
    task = asyncio.create_task(charge("B"))     # scheduled, not yet running
    print("created task, done =", task.done())
    print(await coro)                           # runs inline inside main's task
    print(await task)

asyncio.run(main())
```

```text
created coroutine: coroutine
created task, done = False
  charge(A) started
  charge(B) started
  charge(A) finished
paid:A
  charge(B) finished
paid:B
```

`await coro` runs the coroutine inline, and when it yields at `sleep(0)` the loop gets a chance to start task B. `await coro` alone never creates concurrency; only tasks do.

### create_task and keeping references

The loop keeps only a weak reference to scheduled tasks. A fire-and-forget `asyncio.create_task(...)` whose result you discard can be garbage-collected before it finishes, and the docs say to keep a reference. If the task fails unobserved you also get `Task exception was never retrieved` at collection time, long after the cause.

```python
import asyncio

background: set[asyncio.Task[None]] = set()

def spawn(coro) -> asyncio.Task[None]:
    task = asyncio.create_task(coro)
    background.add(task)                        # strong reference
    task.add_done_callback(background.discard)  # release when finished
    return task

async def audit(event: str) -> None:
    await asyncio.sleep(0.01)
    print("audited", event)

async def main() -> None:
    spawn(audit("order.created"))
    spawn(audit("order.paid"))
    print("in flight:", len(background))
    await asyncio.gather(*background)
    await asyncio.sleep(0)
    print("in flight after:", len(background))

asyncio.run(main())
```

```text
in flight: 2
audited order.created
audited order.paid
in flight after: 0
```

For work whose lifetime is bounded by a request or a job, prefer a `TaskGroup` over this pattern; the set-plus-callback idiom is for genuinely detached work, and it is the seed of a task supervisor (the assignment at the end of this lesson).

### gather versus TaskGroup

`asyncio.gather(*aws)` without `return_exceptions=True` propagates the first exception to the awaiter but does **not** cancel the other awaitables; they keep running and spending money. `asyncio.TaskGroup` (3.11+) enforces structured concurrency: when any child fails, the group cancels the remaining children, waits for them, and raises an `ExceptionGroup` that you handle with `except*`.

```python
import asyncio

async def provider(name: str, delay: float, fail: bool = False) -> str:
    try:
        await asyncio.sleep(delay)
        if fail:
            raise RuntimeError(f"{name} failed")
        print(f"  {name} finished")
        return name
    except asyncio.CancelledError:
        print(f"  {name} cancelled")
        raise

async def with_gather() -> None:
    print("gather:")
    try:
        await asyncio.gather(
            provider("openai", 0.05, fail=True),
            provider("anthropic", 0.15),
            provider("local", 0.25),
        )
    except RuntimeError as exc:
        print("  caught:", exc)
    await asyncio.sleep(0.3)   # observe what the siblings do afterwards

async def with_taskgroup() -> None:
    print("TaskGroup:")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(provider("openai", 0.05, fail=True))
            tg.create_task(provider("anthropic", 0.15))
            tg.create_task(provider("local", 0.25))
    except* RuntimeError as eg:
        print("  caught:", [str(e) for e in eg.exceptions])

asyncio.run(with_gather())
asyncio.run(with_taskgroup())
```

```text
gather:
  caught: openai failed
  anthropic finished
  local finished
TaskGroup:
  local cancelled
  anthropic cancelled
  caught: ['openai failed']
```

The order in which the group cancels siblings is not specified, so never depend on it. Two details matter: a plain `except RuntimeError:` does not catch what a `TaskGroup` raises, because it raises an `ExceptionGroup`; and `except*` can match a subset and let the rest propagate. `gather(..., return_exceptions=True)` is still the right tool when you want every outcome, success or failure, as data.

### Cancellation

`task.cancel()` does not kill a task. It schedules a `CancelledError` to be thrown into the coroutine at its next suspension point. `CancelledError` derives from `BaseException` (since 3.8), so `except Exception` does not swallow it, but a bare `except:` or `except BaseException:` does. Rules a senior engineer follows:

- Put cleanup in `finally`, or catch `CancelledError`, clean up, and **re-raise**. Swallowing it leaves a task that looks finished but ignored the caller's request; a `timeout()` or `TaskGroup` that depends on the cancellation then misbehaves.
- Cleanup that itself awaits can be cancelled again. Wrap truly must-finish cleanup (releasing a seat, committing an offset) in `asyncio.shield(...)`.
- `asyncio.shield(aw)` protects the inner awaitable from cancellation of the *outer* await, but the outer caller still sees `CancelledError`, and the inner task must be kept referenced by you.

```python
import asyncio

async def reserve_seat(ledger: list[str]) -> None:
    ledger.append("seat held")
    try:
        await asyncio.sleep(10)            # waiting on a payment provider
    finally:
        await asyncio.shield(release(ledger))   # survives a second cancel

async def release(ledger: list[str]) -> None:
    await asyncio.sleep(0.01)
    ledger.append("seat released")

async def main() -> None:
    ledger: list[str] = []
    task = asyncio.create_task(reserve_seat(ledger))
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        ledger.append("CancelledError reached caller")
    print(ledger, "| task.cancelled() =", task.cancelled())

asyncio.run(main())
```

```text
['seat held', 'seat released', 'CancelledError reached caller'] | task.cancelled() = True
```

> **Pitfall:** `asyncio.wait_for(asyncio.shield(t), 0.05)` times out without cancelling `t`, which is sometimes exactly what you want (let the slow LLM call finish and cache it) and sometimes a leak. Decide deliberately.

### Timeouts

`asyncio.timeout(delay)` (3.11+) is an async context manager. On expiry it cancels the *current task*, and on exit converts that cancellation into `TimeoutError`. Since 3.11 `asyncio.TimeoutError` is an alias of the builtin `TimeoutError`. The manager exposes `expired()` and `reschedule()`, and `asyncio.timeout_at()` takes an absolute loop time, which composes better across several calls sharing one deadline than repeating `wait_for(..., t)`.

```python
import asyncio

async def slow_llm_call() -> str:
    try:
        await asyncio.sleep(1)
        return "tokens"
    finally:
        print("  slow_llm_call cleanup ran")

async def main() -> None:
    try:
        async with asyncio.timeout(0.05) as cm:
            await slow_llm_call()
    except TimeoutError:
        print("timed out; cm.expired() =", cm.expired())

asyncio.run(main())
```

```text
  slow_llm_call cleanup ran
timed out; cm.expired() = True
```

Because the timeout is implemented with cancellation, code inside the block that swallows `CancelledError` defeats it: the block finishes normally and no `TimeoutError` is raised.

### asyncio.run, debug mode and lost coroutines

`asyncio.run(main())` creates a fresh loop, runs `main`, cancels any leftover tasks, shuts down async generators and the default executor, and closes the loop. Calling it from inside a running loop raises `RuntimeError: asyncio.run() cannot be called from a running event loop`, a classic error when a sync helper is called from an async endpoint.

Two bug classes hide silently. Calling a coroutine function without `await` produces `RuntimeWarning: coroutine '...' was never awaited`. A task whose exception nobody retrieves logs `Task exception was never retrieved` at garbage collection. Run with `python -X dev` (or `PYTHONASYNCIODEBUG=1`, or `asyncio.run(main(), debug=True)`) to turn on debug mode, which adds creation tracebacks:

```text
<stdin>:7: RuntimeWarning: coroutine 'send_receipt' was never awaited
Coroutine created at (most recent call last)
  ...
Task exception was never retrieved
future: <Task finished name='Task-2' coro=<main.<locals>.boom() done, ... exception=ValueError('lost') ...>
```

In CI, promote warnings to errors (for pytest, run with `-W error`) so a forgotten `await` fails the build instead of scrolling past in the logs.

### Structured concurrency

The principle is that a child task's lifetime is nested inside its parent's scope: nothing outlives the `async with` block that started it, errors flow up, and cancellation flows down. `TaskGroup` plus `timeout` gives you that, and it composes: a deadline around a group cancels the whole tree, and each child's `finally` runs before the exception leaves.

## Practical Backend Scenario

Your LLM gateway must answer within 2 seconds. It can call three providers, and the first successful answer wins. The losers must be cancelled promptly, because each in-flight request keeps a connection open and may bill for generated tokens. If all fail, the caller needs every failure for logging; if the deadline passes, everything must stop.

```python
import asyncio
from collections.abc import Awaitable, Callable

type Provider = Callable[[str], Awaitable[str]]

async def first_success(
    prompt: str, providers: dict[str, Provider], deadline: float
) -> tuple[str, str]:
    """Race providers; return (name, answer) of the first success and cancel the rest."""
    loop = asyncio.get_running_loop()
    outcome: asyncio.Future[tuple[str, str] | None] = loop.create_future()
    failures: list[Exception] = []

    async def attempt(name: str, call: Provider) -> None:
        try:
            answer = await call(prompt)
        except Exception as exc:                 # CancelledError is not an Exception
            failures.append(exc)
            if len(failures) == len(providers) and not outcome.done():
                outcome.set_result(None)         # nobody can win any more
            return
        if not outcome.done():
            outcome.set_result((name, answer))

    async with asyncio.timeout(deadline):
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(attempt(n, c)) for n, c in providers.items()]
            winner = await outcome
            for task in tasks:
                task.cancel()                    # losers run their finally blocks
    if winner is None:
        raise ExceptionGroup("all providers failed", failures)
    return winner
```

Running it against a fast provider, a slow one with a `finally` that prints "slow provider cleaned up", and a broken one returns `('fast', 'fast:hi')` and the slow provider's cleanup runs. With two broken providers the caller gets an `ExceptionGroup` of 2 `ConnectionError`s, and with only a slow provider and a 0.05 s deadline it gets `TimeoutError` after the cleanup runs. Note the design choice: `except Exception` in `attempt` records provider failures without ever swallowing cancellation, and the exception group is raised outside the `TaskGroup`, so it is not wrapped in a second group.

## Practice Loop

1. Re-type the heartbeat example and measure it with `time.sleep` versus `asyncio.sleep`; then replace the blocking call with `await asyncio.to_thread(time.sleep, 0.3)` and observe the heartbeat again.
2. Reproduce the `gather` versus `TaskGroup` difference and add a `finally` to the provider that records whether it was cancelled.
3. Run the un-awaited coroutine snippet with `python -X dev` and compare the output with a plain run; note the extra creation tracebacks.
4. Write a coroutine that swallows `CancelledError` inside `asyncio.timeout(0.05)` and predict, then verify, what the block does.
5. Implement `first_success` from memory, then add a metric counter for cancelled losers.
6. Complete the two coding assignments below with tests that assert cleanup ran, not only that results were correct.

## Evidence of Understanding

- I can explain why `await coro` does not create concurrency and `create_task` does.
- I can state what `gather` leaves running after a failure and what `TaskGroup` does instead.
- I can write cancellation-safe cleanup that re-raises `CancelledError` and shields the must-finish step.
- I can predict that swallowing `CancelledError` inside `asyncio.timeout` suppresses the `TimeoutError`.
- I can handle a `TaskGroup` failure with `except*` and explain why plain `except` misses it.
- I can diagnose a "never awaited" warning and a "never retrieved" exception from their text alone.

## Interview Questions to Rehearse

### Q: What is the difference between a coroutine, a Task and a Future?
A coroutine object is an unstarted suspended frame returned by calling an `async def`. A Task wraps a coroutine, schedules it on the loop and drives it to completion, so it runs concurrently with whoever created it. A Future is a passive result container resolved by someone else, and Task is a Future subclass. Awaiting a bare coroutine runs it inline in the current task and adds no concurrency.

### Q: Why might a fire-and-forget `create_task` call fail intermittently in production?
The loop holds only weak references to tasks, so a task nobody references can be garbage-collected before it finishes, and an unobserved exception surfaces late as "Task exception was never retrieved". Keep tasks in a set with a done callback that discards them and reports errors, or give them an owner such as a `TaskGroup`.

### Q: How do `gather` and `TaskGroup` differ on failure?
`gather` raises the first exception to the awaiter but leaves the other awaitables running unless you cancel them. `TaskGroup` cancels the remaining children when one fails, waits for them to finish, and raises an `ExceptionGroup` handled with `except*`. `TaskGroup` gives structured concurrency; `gather(return_exceptions=True)` is for collecting all outcomes.

### Q: What happens when you cancel a task, and what must your code do?
`cancel()` requests cancellation; a `CancelledError` is raised at the task's next await. It is a `BaseException`, so `except Exception` lets it through. Code should clean up in `finally` or catch, clean up and re-raise, and never swallow it. Must-finish cleanup that awaits should be shielded, because it can be cancelled again. Swallowing cancellation also breaks `timeout()` and `TaskGroup`, which rely on it.

### Q: How does `asyncio.timeout` work, and how does it differ from `wait_for`?
It schedules a call that cancels the current task at the deadline, and on exit converts that cancellation into `TimeoutError`. It wraps a block of several awaits under one deadline, can be rescheduled, and `timeout_at` shares an absolute deadline. `wait_for` wraps one awaitable. Both need non-swallowed cancellation to work.

### Q: A teammate calls `asyncio.run()` inside a FastAPI endpoint. What happens and what do you do?
It raises `RuntimeError: asyncio.run() cannot be called from a running event loop`. The endpoint is already on a running loop, so make the helper async and `await` it, or run genuinely blocking sync code with `asyncio.to_thread`.

## Common Pitfalls

- `except Exception` is safe for cancellation, but bare `except:` and `except BaseException:` swallow `CancelledError`, so timeouts and shutdowns stop working.
- Forgetting `await` on a coroutine call; the warning appears only at garbage collection, so run tests with warnings as errors.
- Treating `gather` as if it cancelled siblings on failure, which leaves paid provider calls running.
- Writing `except ValueError` around a `TaskGroup` and missing the `ExceptionGroup`; use `except*`.
- Calling blocking code (`time.sleep`, `requests.get`, large JSON parsing, CPU loops) in a coroutine; every task on the loop stalls.
- Assuming `asyncio.gather(cpu(), cpu())` parallelises CPU work; coroutines without an `await` run one after another on one thread.
- Dropping the task reference returned by `create_task`.

## Suggested Extension

Build an async job runner that accepts a list of jobs, runs them under a `TaskGroup` with a global deadline, and records for each job whether it succeeded, failed, or was cancelled. Add a test that proves a cancelled job's `finally` block ran before the runner returned, and a second test showing what happens to the runner's deadline when one job swallows `CancelledError`.
