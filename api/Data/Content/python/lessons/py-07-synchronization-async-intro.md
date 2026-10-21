# Synchronization and an Introduction to Async

Threads share memory, and that is both their power and their danger. The moment two threads touch the same mutable state, you need a discipline: what is protected, by which lock, in what order, and how the others wait. This lesson covers the primitives (`Lock`, `RLock`, `Condition`, `Semaphore`, `Barrier`, `Queue`), the failure modes (races, deadlock, lost wake-ups), and the first step into `asyncio`, which removes much of this machinery by changing where context switches can happen. Interviewers love this topic because a ten-line snippet reveals whether you reason about interleavings or just hope.

## Concepts Covered

### Race conditions and check-then-act

A race condition exists when correctness depends on how threads interleave. `counter += 1` compiles to separate load, add and store steps. The GIL guarantees that a single bytecode is atomic, not that a sequence of them is. Individual operations like `list.append` or `dict[key] = value` are atomic in CPython, but check-then-act sequences (`if seats >= n: seats -= n`) and read-modify-write are not, and free-threaded builds make this stricter, not looser.

A caution on demos: on CPython 3.12 and later a bare `counter += 1` in a tight loop rarely loses updates on a given machine, because thread switches are only considered at specific points. That does not make it safe. Any call, I/O, logging or allocation between the read and the write is a possible switch point, and production code always has one. The demo below makes the switch point explicit with `time.sleep(0)`:

```python
import threading
import time

class Account:
    def __init__(self) -> None:
        self.balance = 0

    def deposit(self, amount: int) -> None:
        current = self.balance            # read
        time.sleep(0)                     # any I/O, logging or call can yield here
        self.balance = current + amount   # write

class SafeAccount(Account):
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()

    def deposit(self, amount: int) -> None:
        with self._lock:
            super().deposit(amount)

def hammer(acct: Account) -> int:
    def work() -> None:
        for _ in range(2_000):
            acct.deposit(1)
    threads = [threading.Thread(target=work) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return acct.balance

print("unsafe:", hammer(Account()), "expected 8000")
print("safe:  ", hammer(SafeAccount()), "expected 8000")
```

```text
unsafe: 2219 expected 8000
safe:   8000 expected 8000
```

The unsafe number differs on every run. The safe one is always 8000.

### Lock, RLock and the shape of a critical section

A `Lock` is a mutex with no owner: any thread may release it, and a thread that tries to acquire it twice blocks itself forever. Always use `with lock:` so release happens on exceptions. `acquire(blocking=False)` and `acquire(timeout=...)` return a bool and are how you build deadlock-tolerant code. An `RLock` records its owner and a recursion count, so the same thread can re-enter, which is what you need when a locked public method calls another locked method. Prefer restructuring (a private `_unlocked` helper) over reaching for `RLock` automatically, because reentrancy hides unclear invariants.

The critical section must include the **check and the update together**. A booking system that checks `available >= n` outside the lock and decrements inside it is still racy: two threads both pass the check, then both decrement. Keep the section small (never hold a lock across network I/O), but never so small that it splits an invariant.

### Deadlock and lock ordering

Deadlock needs four conditions, and breaking any one removes it: mutual exclusion, hold-and-wait, no pre-emption, and circular wait. In practice you break **circular wait** with a global lock order, or **hold-and-wait** with timeouts. The classic is a transfer between two wallets from opposite directions.

```python
import threading

class Wallet:
    def __init__(self, name: str, balance: int) -> None:
        self.name, self.balance = name, balance
        self.lock = threading.Lock()

def transfer_naive(src: Wallet, dst: Wallet, amount: int, barrier: threading.Barrier) -> str:
    with src.lock:
        barrier.wait()                        # force the unlucky interleaving
        if not dst.lock.acquire(timeout=0.3):
            return f"{src.name}->{dst.name}: gave up (circular wait)"
        try:
            src.balance -= amount
            dst.balance += amount
            return "ok"
        finally:
            dst.lock.release()

def transfer_ordered(src: Wallet, dst: Wallet, amount: int) -> None:
    first, second = sorted((src, dst), key=lambda w: w.name)   # one global order
    with first.lock, second.lock:
        src.balance -= amount
        dst.balance += amount
```

Run `transfer_naive(a, b, ...)` and `transfer_naive(b, a, ...)` concurrently and each thread holds one lock while waiting for the other: at least one reports "gave up". Without the timeout both would hang forever. `transfer_ordered` always takes locks in name order, so a cycle is impossible. In real code the ordering key is a stable id, never `id()` of a transient object. To diagnose a live hang, use `faulthandler.dump_traceback_later(...)` or `py-spy dump --pid`, and look for threads parked in `acquire`.

### Event, Condition and the wait-in-a-loop rule

`Event` is a one-bit flag threads can `wait()` on, ideal for "shutdown requested" or "model loaded". `Condition` combines a lock with a wait queue: you hold the lock, check a predicate, and `wait()` releases the lock atomically while sleeping. Two rules apply: **always re-check the predicate in a loop** (or use `wait_for(predicate)`), because wake-ups can be spurious and another consumer may have taken the item; and **change state before notifying**. `notify()` wakes one waiter, `notify_all()` wakes all and is the safe default when different waiters wait on different predicates.

```python
import threading
from collections import deque

class BoundedBuffer[T]:
    def __init__(self, capacity: int) -> None:
        self._items: deque[T] = deque()
        self._capacity = capacity
        self._cond = threading.Condition()

    def put(self, item: T) -> None:
        with self._cond:
            self._cond.wait_for(lambda: len(self._items) < self._capacity)
            self._items.append(item)
            self._cond.notify_all()

    def get(self) -> T:
        with self._cond:
            self._cond.wait_for(lambda: self._items)
            item = self._items.popleft()
            self._cond.notify_all()
            return item
```

### Semaphore, BoundedSemaphore and Barrier

A `Semaphore(n)` is a counter of permits: `acquire()` blocks at zero, `release()` adds one. Used with `n > 1`, it caps concurrency, for example at most 3 concurrent calls to a rate-limited API. Used with `n = 0`, it is a **signal between threads**: one thread blocks in `acquire()` until a different thread calls `release()`. That is how ordering problems such as "print first, second, third" or "alternate foo and bar" are solved. `BoundedSemaphore` raises `ValueError` if released beyond its initial value, which catches unbalanced releases. A `Barrier(parties, action=None)` makes N threads wait for each other, useful for "all shards loaded before serving". If one party times out or `abort()` is called, everyone gets `BrokenBarrierError`.

```python
import threading

class InOrder:
    def __init__(self) -> None:
        self._after_first = threading.Semaphore(0)
        self._after_second = threading.Semaphore(0)
        self.output: list[str] = []

    def first(self) -> None:
        self.output.append("first")
        self._after_first.release()

    def second(self) -> None:
        self._after_first.acquire()          # blocks until first() releases
        self.output.append("second")
        self._after_second.release()

    def third(self) -> None:
        self._after_second.acquire()
        self.output.append("third")
```

Starting the threads in the order third, second, first still produces `['first', 'second', 'third']`. A bug to watch for: initialising the semaphore to 1 instead of 0 lets `second()` run without waiting.

### queue.Queue: prefer message passing over shared state

`queue.Queue` bundles the lock, the condition variables and the buffer. `put` blocks when a bounded queue is full (backpressure), `get` blocks when empty, and `task_done()` plus `join()` let a producer wait until every item has been processed. Shut consumers down with a sentinel ("poison pill") per consumer. Since 3.13, `Queue.shutdown()` does this properly: `put` raises `queue.ShutDown` immediately, and `get` raises it once the queue is drained. `PriorityQueue`, `LifoQueue` and `SimpleQueue` cover other orders. The principle "do not communicate by sharing memory, share memory by communicating" removes most locks from your own code.

```python
import queue
import threading

q: queue.Queue[int | None] = queue.Queue(maxsize=4)
results: list[int] = []
guard = threading.Lock()

def worker() -> None:
    while True:
        item = q.get()
        try:
            if item is None:
                return
            with guard:
                results.append(item * item)
        finally:
            q.task_done()     # always, or join() never returns

workers = [threading.Thread(target=worker) for _ in range(3)]
for w in workers:
    w.start()
for i in range(10):
    q.put(i)                  # blocks when 4 items are waiting
for _ in workers:
    q.put(None)
q.join()
print(sorted(results))
```

```text
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### First steps with asyncio

`async def` defines a coroutine function. Calling it returns a coroutine object and runs nothing. `await` suspends the current coroutine and hands control back to the **event loop**, a single-threaded scheduler, until the awaited thing completes. `asyncio.run(main())` creates a loop, runs `main`, and closes it. `asyncio.gather(*coros)` runs coroutines concurrently as tasks and returns results in argument order, and `asyncio.create_task` schedules one without waiting.

```python
import asyncio
import time

async def call_model(name: str, delay: float) -> str:
    print(f"{name}: start")
    await asyncio.sleep(delay)
    print(f"{name}: done")
    return name.upper()

async def main() -> None:
    t0 = time.perf_counter()
    results = await asyncio.gather(call_model("a", 0.3), call_model("b", 0.2), call_model("c", 0.1))
    print(results, f"{time.perf_counter() - t0:.1f}s")

asyncio.run(main())
```

```text
a: start
b: start
c: start
c: done
b: done
a: done
['A', 'B', 'C'] 0.3s
```

Three waits overlap, so the total is the longest, not the sum. Switches happen only at `await`, which is why async code needs far fewer locks: there is no preemption between awaits. But the same check-then-act bug reappears **across** an `await`: read a value, await something, write it back, and another task may have changed it. For that, `asyncio.Lock`, `asyncio.Semaphore` and `asyncio.Queue` mirror the threading API but are awaited (`async with sem:`) and are **not** thread-safe. The cardinal rule is never to block the loop: one `time.sleep(0.3)` or synchronous HTTP call stalls every task. Offload it with `await asyncio.to_thread(fn, ...)` (which uses the executors from the previous lesson).

```python
import asyncio
import time

async def ticker(stop: asyncio.Event) -> float:
    worst, last = 0.0, time.perf_counter()
    while not stop.is_set():
        await asyncio.sleep(0.01)
        now = time.perf_counter()
        worst = max(worst, now - last)
        last = now
    return worst

async def measure(blocker) -> float:
    stop = asyncio.Event()
    t = asyncio.create_task(ticker(stop))
    await asyncio.sleep(0.05)
    await blocker()
    stop.set()
    return await t

async def blocking() -> None:
    time.sleep(0.3)                                  # freezes the loop

async def offloaded() -> None:
    await asyncio.to_thread(time.sleep, 0.3)         # loop stays responsive
```

```text
time.sleep        -> worst loop stall 0.3s
asyncio.to_thread -> worst loop stall 0.0s
```

> **Interview tip:** Async is not "faster threads". It wins on many mostly-idle connections (low memory, no per-thread stack, cheap switches), and loses on CPU-bound work, where it behaves like one thread. Say which resource is the bottleneck before choosing.

## Practical Backend Scenario

An LLM gateway receives bursts of chat requests and forwards each to a model provider that allows 8 concurrent calls and returns 429 above that. A thread-per-request design with a shared `dict` of in-flight counters corrupts the counter under load, and a lock held across the provider call serialises everything. The right design is a `Semaphore(8)` (threading, or `asyncio.Semaphore` if the service is async) around only the outbound call, a bounded `Queue` between the HTTP layer and a fixed pool of workers so overload becomes visible backpressure (reject or shed requests) instead of unbounded memory growth, and a shutdown signal (`Event` or `Queue.shutdown()`) that lets in-flight calls drain. A second incident is classic: two background jobs lock the `conversation` and `billing` records in opposite order and hang once a week. The fix is a documented lock order plus a timeout that logs and alerts.

## Practice Loop

1. Reproduce the lost-update race with the `Account` example. Run it five times and record the unsafe totals, then fix it with a `Lock` and prove it with 8 threads.
2. Write a `reserve(n)` method that checks and decrements `available_seats` under one lock. Then deliberately move the check outside the lock and write a test that exposes the overbooking.
3. Reproduce the wallet deadlock with `Barrier`, then fix it two ways: lock ordering and `acquire(timeout=...)` with retry. Use `faulthandler.dump_traceback_later(2)` to see the stuck threads.
4. Implement `FooBar(n)` with two semaphores so the output is `foobar` repeated `n` times. Change an initial value from 0 to 1 and describe the failure.
5. Build the bounded buffer with `Condition`, then replace it with `queue.Queue` and compare the code size and the correctness risks.
6. Convert the producer and consumer to `asyncio.Queue`. Add a blocking `time.sleep` to one consumer, measure the stall, and fix it with `asyncio.to_thread`.

## Evidence of Understanding

- I can explain why a check-then-act sequence is racy even though each bytecode is atomic, and write the minimal critical section.
- I can name the four deadlock conditions and break one of them in code, using lock ordering or a timeout.
- I can explain why `Condition.wait` must be called in a loop and why `notify_all` is the safe default.
- I can use `Semaphore(0)` for signalling and `Semaphore(n)` for capacity, and explain the difference.
- I can describe when `Queue` replaces locks entirely and how to shut consumers down cleanly.
- I can explain where an `asyncio` program can still race, and why one blocking call stalls every task.

## Interview Questions to Rehearse

### Q: Why is `if self.seats >= n: self.seats -= n` unsafe even with the GIL?

The GIL makes each bytecode atomic but can switch threads between the comparison and the subtraction. Two threads both pass the check and both subtract, overbooking the seats. The check and the update must be inside the same critical section, or I use a single atomic primitive such as a database `UPDATE ... WHERE seats >= n`.

### Q: Lock versus RLock: when is each right?

A `Lock` is faster and simpler but cannot be re-acquired by its holder, so a locked method calling another locked method deadlocks. `RLock` allows re-entry by the owner. I use `RLock` only when re-entrancy is genuinely required, such as recursive structures, and otherwise factor out an unlocked internal helper so the invariant is explicit.

### Q: How do you prevent and diagnose deadlock?

Prevent it with a single global lock order, with `acquire(timeout=...)` plus back-off, or by avoiding nested locks via message passing. Diagnose by dumping all thread stacks (`faulthandler`, `py-spy dump`) and looking for the cycle: thread A holds X and waits on Y while thread B holds Y and waits on X.

### Q: Why should `Condition.wait()` be in a `while` loop?

Between being notified and re-acquiring the lock, another thread may have consumed the item, and implementations may wake spuriously. The predicate must be re-checked, which is why `wait_for(predicate)` exists. A bare `if` leads to consuming from an empty buffer.

### Q: When would you choose asyncio over threads, and what is the main risk?

For many concurrent, mostly-waiting I/O connections, where per-thread stacks and switching would dominate. The main risk is blocking the event loop with synchronous calls, which stalls every task. I offload unavoidable blocking work with `asyncio.to_thread` or a process pool, and I still guard multi-step updates that span an `await`.

### Q: What is the difference between `Semaphore(0)` and a `Lock`?

A lock has an owner semantic: the thread that acquires it is expected to release it, and it protects a critical section. `Semaphore(0)` is a signalling counter: one thread waits and another releases, so it passes permission between threads. That is how you enforce ordering.

## Common Pitfalls

- Locking only the write and not the read-check that decides it.
- Holding a lock while doing network or disk I/O, which turns a mutex into a throughput cap.
- Acquiring locks in inconsistent order across code paths.
- Forgetting `task_done()` in a `finally`, so `queue.join()` hangs forever.
- Using `if` instead of `while` or `wait_for` around `Condition.wait()`.
- Initialising an ordering semaphore to 1 instead of 0.
- Calling `time.sleep`, `requests.get` or a blocking DB driver inside a coroutine.
- Calling `asyncio.Queue` or `asyncio.Lock` methods from another thread. They are not thread-safe; use `loop.call_soon_threadsafe` or `asyncio.run_coroutine_threadsafe`.
- Creating a coroutine and never awaiting it (`RuntimeWarning: coroutine ... was never awaited`).

## Suggested Extension

Implement a thread-safe `RateLimiter` (token bucket) with a `Condition`, with `acquire(timeout)` returning a bool. Then port it to `asyncio` using `asyncio.Condition` and compare how the two versions handle cancellation and shutdown.
