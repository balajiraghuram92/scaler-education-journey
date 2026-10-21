# Processes, Threads and the GIL

"Python has a GIL, so threads are useless" is the half-truth that sinks candidates in AI and backend interviews. Threads are exactly right for the I/O-bound fan-out that dominates LLM gateways and document pipelines, and exactly wrong for CPU-bound parsing or embedding preprocessing. What the interviewer wants is the mechanism: what the GIL protects, when it is released, why it does not make your code thread-safe, what `multiprocessing` costs, and what changes in free-threaded CPython.

## Concepts Covered

### Concurrency, parallelism and the three models

**Concurrency** is structuring work so several tasks make progress in overlapping time, even on one core. **Parallelism** is tasks executing at the same instant on different cores. A **thread** is a path of execution inside a process that shares its memory; a **process** has its own interpreter and memory. Python gives you three tools: threads (shared memory, preemptive switching), processes (isolated memory, true parallelism for Python code) and `asyncio` (one thread, cooperative switching at `await`, covered in later lessons). Choosing among them starts with one question: is the task waiting or computing?

### Threads: lifecycle, results and errors

A `Thread` runs its `target` (or an overridden `run()`) once `start()` is called. `join()` blocks the caller until it finishes. Three details interviewers probe: calling `run()` directly executes in the **calling** thread with no concurrency at all; `args` must be a tuple, so `args=("D101")` is just a string whose characters become four arguments; and an exception inside a thread does not propagate to `join()`. It goes to `threading.excepthook`, prints a traceback, and the thread ends. Keep the result and the error on the thread object and re-raise them in the joiner.

```python
import math
import threading

class FactorialThread(threading.Thread):
    def __init__(self, n: int) -> None:
        super().__init__(name=f"fact-{n}")
        self.n = n
        self.result: int | None = None
        self.error: BaseException | None = None

    def run(self) -> None:
        try:
            self.result = math.factorial(self.n)
        except BaseException as exc:             # surface it in the joining thread
            self.error = exc

    def join_result(self, timeout: float | None = None) -> int:
        self.join(timeout)
        if self.is_alive():
            raise TimeoutError(self.name)
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result

t = FactorialThread(20)
t.start()
print(t.join_result())        # 2432902008176640000
bad = FactorialThread(-1)
bad.start()
bad.join_result()             # ValueError: factorial() not defined for negative values
```

Forgetting `join()` is not an error; the program simply continues, and the interpreter waits for non-daemon threads at exit. Daemon threads are killed abruptly at shutdown, so never put work that must complete (a payment write) on one.

### What the GIL protects, and when it is released

The Global Interpreter Lock is a mutex inside CPython that lets only one thread execute Python bytecode at a time. It exists because CPython's memory management (reference counts, the allocator, interpreter state) is not thread-safe, and one coarse lock is cheap and keeps C extensions simple. The consequences are narrower than the folklore:

- CPU-bound pure-Python code gains nothing from threads, since only one runs at a time.
- The lock is **released** while a thread blocks on I/O (`socket`, files, `time.sleep`, `queue.get`) and inside many C extensions that opt out for long calls (`hashlib` on large buffers, `zlib`, NumPy kernels, most database drivers).
- The interpreter forces a handoff after a switch interval (`sys.getswitchinterval()`, 5 ms by default) at safe points between bytecodes.

Measuring beats arguing. On a 32-core machine under CPython 3.13 with the GIL (your numbers will differ, the shape will not):

```python
import hashlib, threading, time

def timeit(label, fn):
    t0 = time.perf_counter(); fn(); print(f"{label}: {time.perf_counter() - t0:.2f}s")

def cpu(n=2_000_000):
    s = 0
    for i in range(n):
        s += i * i

def in_threads(fn, k=4, *args):
    ts = [threading.Thread(target=fn, args=args) for _ in range(k)]
    for t in ts: t.start()
    for t in ts: t.join()

data = b"x" * 50_000_000
timeit("cpu serial x4 ", lambda: [cpu() for _ in range(4)])
timeit("cpu threads x4", lambda: in_threads(cpu))
timeit("io serial x5  ", lambda: [time.sleep(0.5) for _ in range(5)])
timeit("io threads x5 ", lambda: in_threads(time.sleep, 5, 0.5))
timeit("hash serial x4", lambda: [hashlib.sha256(data).digest() for _ in range(4)])
timeit("hash threads x4", lambda: in_threads(lambda: hashlib.sha256(data).digest()))
```

```text
cpu serial x4 : 0.50s
cpu threads x4: 0.52s        # no speedup, slight overhead
io serial x5  : 2.50s
io threads x5 : 0.50s        # waits overlap
hash serial x4: 0.17s
hash threads x4: 0.05s       # the C code released the GIL
```

### The GIL does not make your code thread-safe

The GIL protects the interpreter, not your invariants. `counter += 1` is a read, an add and a write (`LOAD_GLOBAL`, `BINARY_OP`, `STORE_GLOBAL`), and a thread switch between them loses an update. There is a subtlety that explains why many demos "fail to fail": since 3.10 the interpreter checks for a pending thread switch only at certain instructions (calls and backward jumps), so the bare `counter += 1` loop often returns the right total on recent CPython. That is an accident of the eval loop, not a guarantee. Put a function call between the read and the write and the lost updates appear:

```python
import threading

counter = 0
lock = threading.Lock()

def one() -> int:
    return 1

def unsafe(n: int) -> None:
    global counter
    for _ in range(n):
        counter += one()               # call between load and store: switch can happen

def safe(n: int) -> None:
    global counter
    for _ in range(n):
        with lock:                     # make read-modify-write one critical section
            counter += one()

def run(fn) -> int:
    global counter
    counter = 0
    ts = [threading.Thread(target=fn, args=(300_000,)) for _ in range(4)]
    for t in ts: t.start()
    for t in ts: t.join()
    return counter

print(run(unsafe), run(unsafe), run(safe))   # e.g. 1014827 1200000 1200000 (unsafe varies; expected 1200000)
```

Single operations such as `list.append` and `dict[key] = value` are atomic under the GIL, but check-then-act sequences (`if k not in d: d[k] = make()`) are not. Use `threading.Lock`, `queue.Queue` or thread-confined data rather than relying on atomicity folklore, because the free-threaded build removes the accident entirely.

### Processes: real parallelism, real costs

`multiprocessing` starts separate interpreters, each with its own GIL and memory, so CPU-bound Python code scales with cores. The price: arguments and results are **pickled** across pipes (lambdas and open sockets fail to pickle), memory is not shared (mutating a global in the child changes nothing in the parent), and startup is heavy.

How a child starts matters. **`spawn`** launches a fresh interpreter and re-imports your main module (default on Windows and macOS). **`fork`** copies the parent's memory (historically the Linux default through 3.13); it is fast but copies locks held by other threads and can deadlock a multi-threaded parent, which is why 3.12 emits a `DeprecationWarning` when you fork a process that has threads. **`forkserver`** uses a clean helper process and becomes the Linux default in 3.14. Because spawn re-imports the main module, process-creating code must sit under `if __name__ == "__main__":`, or every child tries to start its own children.

```python
import multiprocessing as mp
import os
from math import isqrt

def count_primes(limit: int) -> int:
    return sum(all(n % d for d in range(2, isqrt(n) + 1)) for n in range(2, limit))

if __name__ == "__main__":
    limits = [200_000, 210_000, 220_000, 230_000]
    print(mp.get_start_method())                 # 'spawn' on Windows/macOS
    with mp.Pool(processes=min(4, os.cpu_count() or 1)) as pool:
        results = pool.map(count_primes, limits)    # ordered results, workers reused
    print(results)
```

Raw `Process` objects need manual `start()`, `join()` and a separate channel (`Queue`, `Pipe`) to get a result back; `Pool.map` and, in the next lesson, `ProcessPoolExecutor` collect results in order and propagate exceptions. Batch work into chunks big enough to amortise pickling: sending a million tiny tasks to a pool is slower than serial code.

### Free-threaded CPython

PEP 703 made the GIL optional. Python 3.13 ships an experimental free-threaded build (`python3.13t`) where threads run bytecode in parallel; check with `sys._is_gil_enabled()`, and note `-X gil=0` or `PYTHON_GIL=0` only work on that build (the standard build refuses with "Disabling the GIL is not supported by this build"). PEP 779 promotes it to officially supported in 3.14. Trade-offs: a single-thread slowdown, C extensions that have not declared support can re-enable the GIL at import, and any code that relied on GIL atomicity now needs real locks. Per-interpreter GILs (3.12, PEP 684) give a third route that a Python-level API will expose later (PEP 734). For interviews: processes today, free-threading as the direction, and "the GIL never made my code safe".

## Practical Backend Scenario

An FDE project processes 50,000 scanned invoices a day: download each PDF from object storage, extract text and call an embedding API. The first version runs serially for hours. Moving the download and API calls to a pool of 32 threads brings it down by an order of magnitude, since both are waits. Text extraction, however, is CPU-bound pure Python, and adding threads there changes nothing. Moving it to a `ProcessPoolExecutor` sized to the core count gives near-linear scaling, until the team notices that each task pickles a 20 MB page image across the pipe. The fix is to pass the object-store key instead of the bytes and let each worker fetch its own data.

## Practice Loop

1. Write `Adder(threading.Thread)` and a `Client.main()` that reads two numbers, starts the thread and joins it. Then remove `join()` and observe the ordering.
2. Create `Adder` and `Subtractor` threads and start both from `main`. Run it 20 times and note the output order is not stable.
3. Implement `FactorialThread` with `result` and `error`, and write `compute_large_factorial(n)` using `join()`.
4. Write `TableCreator(threading.Thread)` for numbers 1 to 5 and explain why table lines interleave.
5. Reproduce `args=("D101")` and read the exception printed by the thread; then fix it.
6. Run the timing harness: CPU work serial versus threads, sleep serial versus threads.
7. Reproduce the lost-update counter with a call in the loop, then fix it with a `Lock`.
8. Run a CPU-bound function with `multiprocessing.Pool.map` and compare with threads. Print `mp.get_start_method()`.

## Evidence of Understanding

- You can state what the GIL protects and give two situations where it is released.
- You can explain why `counter += 1` needs a lock even with a GIL.
- You can choose threads, processes or asyncio for a workload and justify it with the waiting-versus-computing test.
- You can explain `spawn`, `fork` and `forkserver`, and why the main guard is mandatory.
- You can say what free-threaded CPython changes and what it does not.

## Interview Questions to Rehearse

### Q: What is the GIL and why does CPython have it?
A mutex that lets only one thread execute Python bytecode at a time. It protects CPython's non-thread-safe internals, notably reference counting, and makes single-threaded code and C extensions fast and simple. It limits CPU parallelism in threads, but it is released during blocking I/O and inside many C extensions.

### Q: Does the GIL make my code thread-safe?
No. It only guarantees that individual bytecodes are not interrupted. `x += 1` is several bytecodes, so updates can be lost, and check-then-act sequences are not atomic. You still need locks, queues or confinement, and in free-threaded builds this is no longer masked.

### Q: Threads or processes for 5 slow API calls? For a CPU-bound transform of 10 million rows?
Threads for the API calls: the GIL is released while waiting, and threads are cheap. Processes (or a native library that releases the GIL, or vectorised NumPy) for the transform, since each process has its own interpreter and GIL. Mention `asyncio` for thousands of connections.

### Q: What goes wrong with `multiprocessing` on Windows or macOS if you forget the main guard?
The `spawn` start method re-imports the main module in each child, so top-level code that creates processes runs again and recurses, leading to a `RuntimeError` or a process explosion. Put process creation under `if __name__ == "__main__":`. Also expect pickling restrictions: no lambdas or locks as arguments.

### Q: Why is forking a multi-threaded process dangerous?
`fork` copies only the calling thread, but it copies memory including locks that other threads held at that instant. The child can deadlock on a lock that nobody will ever release. This is why 3.12 warns, and why `spawn` or `forkserver` is preferable once threads exist.

### Q: What changes with the free-threaded build?
Threads can run Python bytecode in parallel, so CPU-bound threading scales, with a single-threaded slowdown and extension compatibility caveats. It is experimental in 3.13 and supported in 3.14. Code that depended on GIL atomicity must use explicit synchronisation.

## Common Pitfalls

- Using threads for CPU-bound pure-Python work and expecting a speedup.
- Calling `thread.run()` instead of `start()`, which silently runs serially in the caller.
- `args=("x")` instead of `args=("x",)`, which fails inside the new thread, not at the call site.
- Assuming `join()` re-raises exceptions from the thread; it does not.
- Updating shared counters or dicts across threads without a lock because "the GIL protects it".
- Starting processes at module top level, or passing lambdas, sockets and locks to a pool.
- Pickling huge arguments per task, so the cost of the pipe exceeds the computation.
- Forking after starting threads and inheriting a held lock.

## Suggested Extension

Build a benchmark script that runs the same CPU-bound and I/O-bound workloads with serial, `ThreadPoolExecutor`, `ProcessPoolExecutor` and `asyncio` strategies, and prints a table of wall time versus worker count. If you can install a free-threaded interpreter (`python3.13t` or 3.14t), run the thread case on it and report the difference.
