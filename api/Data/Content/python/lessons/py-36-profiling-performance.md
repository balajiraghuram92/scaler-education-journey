# Profiling and Performance Engineering

Most Python performance problems in production are not "Python is slow"; they are an accidental O(n²), a blocking call on the hot path, a cache that never hits, or an allocation pattern that blows up memory. Fixing them starts with measuring, because intuition about where time goes is usually wrong. In interviews this topic shows whether you optimize with evidence and a ladder of options (algorithm, library, vectorize, cache, parallelize, native code) or by guesswork.

## Concepts Covered

### Measure first: `timeit`, wall clock versus CPU time

`timeit` runs a statement many times with garbage collection disabled and a high-resolution clock, which makes it the right tool for comparing two small implementations. Use `timeit.repeat` and take the **minimum**: noise from the OS only ever adds time, so the minimum is the best estimate of the code's real cost. For timing a section in an application use `time.perf_counter()` (monotonic, highest resolution), never `time.time()`, which can jump.

```python
import timeit

ids_list = list(range(10_000))
ids_set = set(ids_list)

t_list = min(timeit.repeat("9_999 in ids_list", globals=globals(), number=2000, repeat=5))
t_set = min(timeit.repeat("9_999 in ids_set", globals=globals(), number=2000, repeat=5))
print(round(t_list / t_set))   # on one run: roughly 1800 (the exact ratio varies)
```

The ratio is the point, not the absolute time. Membership in a list is a linear scan; in a set it is a hash lookup. Always benchmark with realistic sizes and data shapes, since a micro-benchmark on 10 items hides the quadratic behaviour that appears at 100,000.

### Find the hot spot: `cProfile` and `pstats`

`cProfile` is a deterministic profiler: it instruments every function call and reports call counts and time. It tells you **where** the time goes, which is a different question from how fast a snippet is. From the shell: `python -m cProfile -o out.prof -s cumtime script.py`, then inspect with `pstats` (or visualize with tools such as snakeviz).

```python
import cProfile, pstats, io

def dedupe_slow(xs):
    out = []
    for x in xs:
        if x not in out:          # linear scan of a list on every item
            out.append(x)
    return out

data = [i % 5000 for i in range(20_000)]

profiler = cProfile.Profile()
profiler.enable()
dedupe_slow(data)
profiler.disable()

buf = io.StringIO()
pstats.Stats(profiler, stream=buf).sort_stats("cumulative").print_stats(3)
print(buf.getvalue())
```

```text
         5002 function calls in 0.46 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.462    0.462    0.463    0.463 app.py:4(dedupe_slow)
     5000    0.001    0.000    0.001    0.000 {method 'append' of 'list' objects}
```

Timings vary by machine. Read the columns carefully: `tottime` is time inside the function itself excluding callees, `cumtime` includes callees, and `ncalls` shows how many times a function ran. Here `dedupe_slow` has a huge `tottime` and no callee to blame, because the cost is the `in` operator scanning the list inside the function. The profile cannot name the line; that is where `line_profiler` (`@profile` on the function, then `kernprof -l -v script.py`) gives per-line timings. Deterministic profilers add overhead per call, which distorts programs made of many tiny calls.

### Profiling a live service: `py-spy`

You cannot always reproduce production load locally. **py-spy** is a sampling profiler that reads the interpreter's memory from outside the process, so it needs no code changes and has low overhead. Useful commands: `py-spy top --pid 1234` (live view), `py-spy dump --pid 1234` (one-time stack dump of every thread, ideal for a hung worker), and `py-spy record -o profile.svg --pid 1234` (a flame graph). Add `--native` to include C frames when the time is inside an extension. In containers, attaching usually requires the `SYS_PTRACE` capability, and it should be granted deliberately.

> **Production note:** For an incident, take a `py-spy dump` of a stuck worker first. It answers "what is every thread doing right now?" in seconds, and it is the fastest way to see a thread blocked on a lock, a socket or a synchronous call inside an async handler.

### Memory: `tracemalloc` and structural savings

`tracemalloc` records where allocations happen. Take a snapshot before and after a workload and compare them to see which source lines grew.

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()

cache = {i: "x" * 100 for i in range(10_000)}      # the workload under suspicion

after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:1]:
    print(stat)
```

```text
app.py:7: size=592 KiB (+592 KiB), count=9744 (+9744), average=62 B
```

(Exact figures differ by version and platform.) Typical structural savings are: use generators instead of materializing lists (a generator object is about 200 bytes regardless of length, a million-element list is about 8 MB of pointers plus the items), use `__slots__` or `dataclass(slots=True)` for millions of small objects, use `array`, `bytes` or NumPy for homogeneous numeric data, and stream files and HTTP bodies instead of loading them. `sys.getsizeof` is shallow, as covered in the memory-model lesson, so use `tracemalloc` for totals.

### Complexity of built-in operations

Choosing the right container is the highest-leverage optimization in Python. Know these costs:

| Operation | list | dict / set | deque |
|---|---|---|---|
| Index `x[i]` | O(1) | O(1) key lookup average | O(n) in the middle, O(1) at ends |
| Append | O(1) amortized | O(1) average insert | O(1) |
| `x in c` | O(n) | O(1) average | O(n) |
| `insert(0, x)` / `pop(0)` | O(n) | not applicable | O(1) `appendleft` / `popleft` |
| Delete by value / `remove` | O(n) | O(1) average | O(n) |
| Sort | O(n log n) | not applicable | not applicable |

The patterns that turn into quadratic time are repeated: a list used as a queue with `pop(0)`, a list used as a set (`if x not in seen_list`), building a string with repeated `s += part` inside a loop (CPython sometimes optimizes it, but not reliably, so use `"".join`), repeated `sorted()` or `min()` of a growing collection (use `heapq` or `bisect`), and nested loops that look something up by a linear search (build a dict index once).

```python
import timeit
from collections import deque

def drain_list(n):
    q = list(range(n))
    while q:
        q.pop(0)

def drain_deque(n):
    q = deque(range(n))
    while q:
        q.popleft()

for n in (20_000, 40_000):
    a = min(timeit.repeat(lambda: drain_list(n), number=1, repeat=3))
    b = min(timeit.repeat(lambda: drain_deque(n), number=1, repeat=3))
    print(n, round(a / b))          # the ratio grows with n: that is the signature of O(n^2) vs O(n)
```

When doubling `n` makes the slow version about four times slower and the fast version about twice, you have confirmed quadratic against linear behaviour empirically.

### Caching, vectorization and the escape hatches

`functools.lru_cache` memoizes pure functions with hashable arguments. Check that it actually helps with `cache_info()`:

```python
import functools

@functools.lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(30)
print(fib.cache_info())
```

```text
CacheInfo(hits=28, misses=31, maxsize=128, currsize=31)
```

Cache only pure, deterministic functions; set a `maxsize` for anything with unbounded inputs; remember the cache lives for the process (and on methods it pins `self`). For per-request, per-user data you usually want an explicit cache with a TTL and invalidation, not `lru_cache`.

**Vectorization** replaces a Python-level loop with one call into compiled code that operates on a whole array. The interpreter overhead of roughly tens of nanoseconds per bytecode disappears into a C loop.

```python
import numpy as np

def py_dist(xs, ys):
    return sum((x - y) ** 2 for x, y in zip(xs, ys))

def np_dist(ax, ay):
    return int(((ax - ay) ** 2).sum())

n = 200_000
xs = list(range(n)); ys = [y + 3 for y in range(n)]
ax = np.arange(n); ay = ax + 3
print(py_dist(xs, ys), np_dist(ax, ay))
```

```text
1800000 1800000
```

On one run the NumPy version was about 14 times faster at this size; larger arrays and heavier math widen the gap. The cost is memory (temporaries) and the need to think in whole-array operations.

When a profile shows a tight numeric loop that vectorization cannot express, the escape hatches in increasing order of effort are: **Numba** (JIT for numeric Python), **Cython** or **mypyc** (typed Python compiled to C), and a native extension written in **Rust** (PyO3 with maturin) or C++ (pybind11). These pay off for inner loops, parsers and codecs, and they add build, packaging and debugging complexity, so reach for them only after algorithmic and library fixes are exhausted. For parallelism, remember the GIL: processes, free-threaded builds or GIL-releasing extensions, as covered in the previous lesson.

## Practical Backend Scenario

A RAG ingestion service deduplicates chunks before embedding. At 5,000 chunks per document it takes seconds; at 50,000 it times out. A `py-spy dump` of the stuck worker shows it inside the `dedupe` function, and `cProfile` on a replay shows nearly all time in that function itself. The code used `if chunk_hash not in seen` where `seen` was a list. Replacing it with `list(dict.fromkeys(hashes))` (order-preserving, linear) cut that stage from roughly a second to a couple of milliseconds in a reproduction with 50,000 items. The next bottleneck, appending embeddings to a list and re-sorting by score each time, was replaced with `heapq.nlargest`. Only then did the team consider batching calls to the model and a process pool. The order mattered: algorithm first, parallelism last.

## Practice Loop

1. Write `dedupe_slow` and `dedupe_fast`, confirm equal output, and time both at 5,000, 20,000 and 50,000 items with `timeit.repeat`. Plot or tabulate how the ratio grows.
2. Profile `dedupe_slow` with `cProfile`, sort by `tottime` and then by `cumulative`, and explain the difference in what each ordering reveals.
3. Install `line_profiler`, decorate the function with `@profile`, run `kernprof -l -v`, and identify the exact slow line.
4. Use `tracemalloc` snapshots around a function that builds a large dictionary and report the top three allocating lines. Then convert it to a generator pipeline and compare peak memory with `tracemalloc.get_traced_memory()`.
5. Compare `list.pop(0)` and `deque.popleft()` at two sizes and verify the quadratic-versus-linear scaling.
6. Add `lru_cache` to a pure function, call it with repeating and non-repeating inputs, and read `cache_info()` for each case.
7. Rewrite a loop-based distance calculation with NumPy and measure the speed-up. Then note the extra memory used by temporaries with `tracemalloc`.

## Evidence of Understanding

- I can state why the minimum of repeated timings is the best estimate and why `perf_counter` is the right clock.
- I can use `cProfile` and `pstats` to find the hot function, and explain `tottime` versus `cumtime`.
- I can explain the difference between deterministic and sampling profilers and when to use `py-spy` on a live service.
- I can diagnose memory growth with `tracemalloc` snapshot comparison.
- I can recite the complexity of list, dict, set and deque operations and spot the common quadratic patterns on sight.
- I can order optimization options: algorithm, data structure, stdlib or library, vectorization, caching, parallelism, native code, and justify the order.

## Interview Questions to Rehearse

### Q: A Python endpoint is slow. How do you approach it?

Reproduce and measure first: get a representative input and a baseline. Use a sampling profiler such as py-spy on the running service, or `cProfile` on a replay, to find the function that dominates. Fix the algorithm or data structure before micro-optimizing, re-measure, and keep a regression benchmark. Only then consider caching, vectorization, concurrency or native code.

### Q: What is the difference between `cProfile`, `py-spy` and `line_profiler`?

`cProfile` is a deterministic function-level profiler built into the standard library, accurate for call counts but with overhead that distorts programs of many tiny calls. `py-spy` is a sampling profiler that attaches externally with very low overhead, suitable for production. `line_profiler` gives per-line timings of selected functions once you know which function is hot.

### Q: Why is `x in some_list` slow inside a loop, and what do you do?

Membership in a list scans linearly, so a loop doing it is O(n²) overall. Convert the lookup collection to a set or dict once, outside the loop, so each check is O(1) on average. If order or duplicates matter, use `dict.fromkeys` or maintain both a list and a set.

### Q: When would you use `lru_cache`, and what are its hazards?

For pure functions with hashable arguments and a bounded input space, such as parsing a config key or computing a derived constant. Hazards: unbounded growth without `maxsize`, stale results if the function reads external state, holding references to arguments (including `self` on methods), and a global cache shared across tenants that can leak data.

### Q: When is vectorization the right fix, and when is it not?

It is right for numeric work over large homogeneous data, because the loop moves into compiled code. It is not right for irregular control flow, small arrays where overhead dominates, or code whose cost is I/O. Temporaries also increase memory, so chunk very large inputs.

### Q: When do you reach for Cython, Numba or Rust?

After a profile shows a small, stable inner loop that dominates and cannot be vectorized or replaced by a better algorithm or library. I would prototype with Numba or Cython for the lowest friction, and use Rust (PyO3) when I need safety, a reusable library or fine-grained parallelism. I would weigh the added build and deployment complexity against the gain, and keep a pure-Python reference implementation for tests.

## Common Pitfalls

- Optimizing without a profile, or profiling a different workload from production.
- Benchmarking tiny inputs, then discovering quadratic behaviour at real sizes.
- Using the mean of timings instead of the minimum, or timing with `time.time()`.
- Reading `cumtime` and blaming a framework function when the real cost is the caller's own loop (high `tottime`).
- Using lists as queues or sets, string concatenation in loops, and repeated sorting.
- Caching functions with side effects or unbounded inputs, or caching methods and leaking instances.
- Reaching for threads or processes before fixing an algorithmic problem.
- Forgetting that profilers and `tracemalloc` slow the program and change timings.

## Suggested Extension

Build a small `perf_report` script that takes a callable and a list of input sizes, measures it with `timeit.repeat` at each size, estimates the empirical growth exponent by fitting log-log slope, and prints "likely O(n)", "O(n log n)" or "O(n²)" with the supporting numbers. Run it against your own `dedupe_slow`, `dedupe_fast` and a list-based queue to validate that the estimator classifies them correctly.
