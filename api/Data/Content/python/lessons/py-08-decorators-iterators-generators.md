# Decorators, Iterators and Generators

Decorators, iterators and generators are the three mechanisms behind most of the "magic" in Python backends: `@app.get`, `@retry`, `@lru_cache`, `for row in cursor`, streaming LLM tokens, `contextlib.contextmanager`. Seniors are expected to know what these desugar to, which traps they carry (lost metadata, broken method binding, exhausted iterators, lazy validation), and how to build lazy pipelines whose memory does not grow with the input. Interviewers probe exactly those seams.

## Concepts Covered

### Closures: the foundation

Functions are objects: you can store, pass and return them. A closure is an inner function that keeps references to variables of its enclosing scope in **cells**, even after the outer function returned. Two consequences matter. First, closures capture *variables*, not values, so `[lambda: i for i in range(3)]` returns three functions that all see the final `i`. Second, assigning to a captured name inside the inner function makes it local unless you declare `nonlocal`, which is why `count += 1` inside an inner `increment` raises `UnboundLocalError`.

### Decorators: what the `@` really does

`@deco` above `def f` means `f = deco(f)`, executed **once, at definition time** (import time for module-level functions). The decorator usually returns a wrapper closure. Stacked decorators apply bottom-up (closest to the function first) but at call time the **top-most is the outermost** wrapper and runs first.

Always use `functools.wraps(fn)` in the wrapper. It copies `__module__`, `__name__`, `__qualname__`, `__doc__` and `__dict__`, and sets `__wrapped__`, which `inspect.signature` follows. Without it, `add.__name__` is `"wrapper"`, docs and tracebacks lie, and frameworks that introspect signatures (FastAPI's dependency injection, pytest fixtures) break. For type checkers, type the wrapper with `ParamSpec` so the decorated function keeps its signature:

```python
import functools
import inspect
import time
from collections.abc import Callable

def timed[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__qualname__} took {(time.perf_counter() - start) * 1000:.0f} ms")
    return wrapper

@timed
def embed(text: str, *, dims: int = 4) -> list[float]:
    """Embed text."""
    time.sleep(0.02)
    return [0.0] * dims

print(embed("hi"))
print(embed.__name__, embed.__doc__, inspect.signature(embed))
```

```text
embed took 20 ms
[0.0, 0.0, 0.0, 0.0]
embed Embed text. (text: str, *, dims: int = 4) -> list[float]
```

### Decorators with arguments

`@repeat(3)` means `repeat(3)` is evaluated first and **returns** the real decorator, which is then applied to the function. That is why parametrised decorators have three layers: factory, decorator, wrapper. A realistic one is a TTL cache with an injectable clock, which makes it testable without sleeping:

```python
import functools
import time
from collections.abc import Callable

def ttl_cache(seconds: float, clock: Callable[[], float] = time.monotonic):
    def decorator[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
        store: dict[tuple, tuple[float, T]] = {}      # one cache per decorated function

        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = (args, tuple(sorted(kwargs.items())))
            now = clock()
            hit = store.get(key)
            if hit is not None and now - hit[0] < seconds:
                return hit[1]
            value = fn(*args, **kwargs)
            store[key] = (now, value)
            return value

        wrapper.cache_clear = store.clear   # type: ignore[attr-defined]
        return wrapper
    return decorator

now = [0.0]
calls: list[str] = []

@ttl_cache(10, clock=lambda: now[0])
def price(sku: str) -> int:
    calls.append(sku)
    return len(sku)

price("abc"); price("abc")      # second call is a cache hit
now[0] = 11
price("abc")                    # expired, recomputed
print(calls)
```

```text
['abc', 'abc']
```

Note the production caveats: the cache is unbounded, keys must be hashable, and a thread-safe version needs a lock. For pure functions prefer `functools.lru_cache(maxsize=...)` or `functools.cache`.

### Class-based decorators and the method-binding trap

A class with `__call__` can be a decorator, and it is the natural choice when the decorator carries state across calls (call counters, circuit-breaker state). Use `functools.update_wrapper(self, func)` in `__init__` to copy metadata. The trap: a class instance is **not a function**, so it has no `__get__` and does not bind `self` when used on a method.

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

class Svc:
    @CountCalls
    def ping(self):
        return "pong"

try:
    Svc().ping()
except TypeError as e:
    print("TypeError:", e)
```

```text
TypeError: Svc.ping() missing 1 required positional argument: 'self'
```

The fix is to implement `__get__` so that attribute access returns a bound callable (for example `functools.partial(self.__call__, obj)` or `types.MethodType(self, obj)`), or to use a function-based decorator, whose wrapper is a plain function and binds automatically. Decorators can also decorate **classes** (take the class, register or modify it, return it), which is how many plugin registries work.

> **Interview tip:** Say "order of decoration is bottom-up, order of execution is top-down". With `@tag("outer")` over `@tag("inner")`, the decoration messages print inner then outer, and at call time you see `enter outer`, `enter inner`, the body, `exit inner`, `exit outer`.

### The iterator protocol

An **iterable** has `__iter__` returning an iterator. An **iterator** has `__next__` and its own `__iter__` returning `self`. `for x in obj` calls `iter(obj)` once, then calls `next()` repeatedly until `StopIteration`. Because an iterator returns itself from `__iter__`, it can be consumed once; a container returns a fresh iterator each time, so it can be looped repeatedly. A class that returns `self` from `__iter__` (like the lecture's `Countdown` and `NumberRange`) is therefore single-pass, a frequent source of "my second loop is empty" bugs. `iter(callable, sentinel)` builds an iterator that calls `callable()` until it returns the sentinel, handy for `iter(partial(f.read, 8192), b"")`.

### Generators: coroutines you can pause

A function with `yield` returns a generator object **without running any of its body**. Each `next()` runs to the next `yield`, keeping locals and the instruction pointer. A `return value` raises `StopIteration(value)`. Generators are also two-way: `send(x)` makes the paused `yield` expression evaluate to `x`, `throw(exc)` raises at the paused point, and `close()` raises `GeneratorExit` there so `try/finally` cleanup runs. A new generator must be primed with `next()` (or `send(None)`) before a non-None `send`.

```python
from collections.abc import Generator

def running_mean() -> Generator[float | None, float, None]:
    total, n = 0.0, 0
    mean: float | None = None
    try:
        while True:
            x = yield mean
            total += x
            n += 1
            mean = total / n
    finally:
        print(f"closed after n={n}")

g = running_mean()
print(next(g))                             # prime: runs to the first yield
print(g.send(10), g.send(20), g.send(30))
g.close()                                  # GeneratorExit at the yield; finally runs
```

```text
None
10.0 15.0 20.0
closed after n=3
```

`yield from sub` delegates to a sub-generator: values, `send`, `throw` and `close` pass through transparently, and the expression's value is the sub-generator's `return` value. That is how you compose generator stages and how `await` was originally built.

```python
def read_batch(items):
    count = 0
    for x in items:
        yield x
        count += 1
    return count

def pipeline():
    n1 = yield from read_batch([1, 2])
    n2 = yield from read_batch([3, 4, 5])
    return n1 + n2
```

Driving `pipeline()` yields 1 to 5 and finishes with `StopIteration(value=5)`. One more trap: input validation inside a generator function runs only on the first `next()`, so `even_numbers(-1)` does not raise when called. If errors must be eager, validate in a normal function and return the inner generator.

### Lazy pipelines with generator expressions and itertools

Chain generators so each stage pulls one item at a time and memory stays flat regardless of input size. `itertools` supplies tested building blocks: `islice`, `chain`, `takewhile`, `accumulate`, `groupby` (only groups *adjacent* equal keys, so sort first), and `batched` (3.12+) to group items for bulk API calls. `tee` buffers the items one consumer has read and another has not, so it is not free. A generator expression `(x*x for x in data)` is single-pass, and `sys.getsizeof` of it is a couple of hundred bytes regardless of length because it stores the recipe, not the values.

```python
import io
import json
from collections import Counter
from collections.abc import Iterable, Iterator
from itertools import batched

raw = io.StringIO("\n".join(
    "corrupt line" if n % 5 == 0 else json.dumps({"tenant": "acme" if n % 3 else "globex", "tokens": n})
    for n in range(1, 13)
))

def read_lines(f: Iterable[str]) -> Iterator[str]:
    for line in f:
        yield line.rstrip("\n")

def parse(lines: Iterable[str], bad: Counter[str]) -> Iterator[dict]:
    for line in lines:
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            bad["unparseable"] += 1

bad: Counter[str] = Counter()
billable = (e for e in parse(read_lines(raw), bad) if e["tokens"] > 3)
usage: Counter[str] = Counter()
for batch in batched(billable, 3):
    for e in batch:
        usage[e["tenant"]] += e["tokens"]
    print(f"flushed batch of {len(batch)}: {[e['tokens'] for e in batch]}")
print(dict(usage), dict(bad))
```

```text
flushed batch of 3: [4, 6, 7]
flushed batch of 3: [8, 9, 11]
flushed batch of 1: [12]
{'acme': 30, 'globex': 27} {'unparseable': 2}
```

The same shape processes a 10 GB log on an 8 GB machine: read line, parse, filter, aggregate, with only one line and one batch alive at a time. When a generator holds a resource (a file, a DB cursor), wrap it in `try/finally` or `with` inside the generator and make sure callers `close()` it or exhaust it, because abandoned generators are only finalised when garbage collected.

## Practical Backend Scenario

Your platform streams a customer's 40 GB export of chat transcripts into an embedding service. A first version does `json.load(...)` and `for chat in chats`, and the worker is OOM-killed. The rewrite is a generator pipeline: `read_lines`, `parse_json` (counting malformed lines in a `Counter`), `redact_pii`, `chunk_words`, then `batched(chunks, 64)` to bulk-call the provider. Memory is constant, one bad line increments a counter instead of failing the job, and a `retry` decorator wraps the provider call while a `ttl_cache` decorator avoids re-embedding identical chunks. A `timed` decorator with `functools.wraps` feeds metrics without hiding the function names from tracing. When the job is cancelled, closing the outermost generator propagates `GeneratorExit` down through `yield from` stages and releases the file handle.

## Practice Loop

1. Write `@count_calls` as a function decorator with an attribute on the wrapper, then as a class. Apply both to a plain function and to a method, and observe which breaks.
2. Remove `functools.wraps` from `timed`, then print `__name__`, `__doc__` and `inspect.signature`. Restore it and compare.
3. Stack two decorators that print on decoration and on call. Predict the output order before running it.
4. Implement `Countdown` as a self-returning iterator and as an iterable that returns a fresh generator from `__iter__`. Loop over each twice.
5. Write `running_mean` with `send`, `throw(ValueError)` to reset it, and `close()`. Add a `finally` that logs.
6. Build the read, parse, filter, batch pipeline over a large generated file and use `tracemalloc` to prove memory is flat.
7. Implement `retry(times, delay=0)` per the coding assignment and test it with a patched `time.sleep`.

## Evidence of Understanding

- I can desugar `@a @b def f` into explicit calls and state both decoration order and call order.
- I can explain what `functools.wraps` copies and what breaks without it.
- I can write a parametrised decorator from memory and explain the three layers.
- I can explain why a class-based decorator breaks on methods and how `__get__` fixes it.
- I can explain iterable versus iterator and predict when a second loop is empty.
- I can use `send`, `throw`, `close` and `yield from`, and explain what `return` in a generator does.
- I can build a lazy pipeline and justify its memory profile.

## Interview Questions to Rehearse

### Q: Why do parametrised decorators need an extra layer?

Because `@repeat(3)` is an expression evaluated first: `repeat(3)` must return the actual decorator, which then receives the function and returns the wrapper. So there are three levels: the factory takes the configuration, the decorator takes the function, and the wrapper takes the call arguments.

### Q: What does `functools.wraps` do and why does it matter in production?

It copies name, qualname, docstring, module and `__dict__` from the wrapped function onto the wrapper and sets `__wrapped__`. Introspection tools, tracebacks, docs and frameworks that read signatures (FastAPI, pytest) depend on that metadata, and without it every decorated function is called `wrapper`.

### Q: When would you use a class-based decorator, and what is the catch?

When the decorator owns mutable state across calls, such as counters or a circuit breaker. The catch is that an instance has no `__get__`, so used on a method it does not receive `self`. I implement `__get__` or use a function decorator with state in a closure or on the wrapper.

### Q: What is the difference between an iterator and an iterable?

An iterable produces an iterator via `__iter__`. An iterator has `__next__` and returns itself from `__iter__`, so it is single-pass. Containers are iterable but not iterators, which lets you loop over them repeatedly. Generators are iterators.

### Q: What do `send`, `throw` and `close` do on a generator, and what is `yield from` for?

`send` resumes the generator and makes the paused `yield` evaluate to the sent value, `throw` raises an exception at that point, and `close` raises `GeneratorExit` so `finally` blocks run. `yield from` delegates to a sub-generator, forwarding all three and returning the sub-generator's return value, which makes composing stages simple.

### Q: How would you process a file larger than memory?

Iterate the file lazily, which yields one line at a time, and chain generator stages (parse, filter, batch). Memory stays proportional to a batch, not the file. I keep stages single-purpose, count and skip bad records instead of failing, and ensure the file handle is closed when the pipeline is abandoned.

## Common Pitfalls

- Forgetting `functools.wraps`, so names, docs and signatures disappear.
- Returning `wrapper()` instead of `wrapper` (calling instead of returning).
- Closures in loops that all capture the final loop variable. Bind with a default argument or `functools.partial`.
- Reading and assigning a captured variable without `nonlocal`, which raises `UnboundLocalError`.
- A class-based decorator applied to a method with no `__get__`.
- Assuming validation inside a generator function runs at call time. It runs at first `next()`.
- Iterating a generator twice and getting an empty second pass.
- Using `groupby` on unsorted data, producing duplicate groups.
- Leaving a generator that holds a file or cursor half-consumed, delaying cleanup until garbage collection.
- Using `itertools.tee` to fan out a huge stream, which buffers everything one branch is ahead.

## Suggested Extension

Write a `@trace` decorator that works on plain functions, `async def` functions and generator functions: detect the kind with `inspect.iscoroutinefunction` and `inspect.isgeneratorfunction`, and wrap each correctly so the span covers the whole run of a generator, not just its creation. Type it with `ParamSpec` and test all three kinds.
