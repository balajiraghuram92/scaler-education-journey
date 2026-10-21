# Design Patterns: Decorator and Flyweight

A model client in production is never just `generate()`. It retries, caches, meters tokens, scans inputs and logs, and the question is whether those concerns live in one tangled class or in layers you can reorder and test separately. Decorator is the pattern that gives you the layers; Flyweight is the pattern you reach for when you have millions of small objects and the memory bill shows up. Both are structural patterns that Python's own idioms (`@decorator`, `__slots__`, `sys.intern`) echo, and interviewers like to probe exactly where the pattern and the idiom diverge.

## Concepts Covered

### Decorator: add behaviour by wrapping, keep the interface

A Decorator wraps an object that implements an interface and implements **the same interface**, adding behaviour before or after delegating. Because the wrapper is itself a valid component, wrappers stack. The client cannot tell how many layers there are. Three ingredients: a component interface, a concrete component, and decorators that hold a component and delegate.

The following layers add retries, caching and metering to any `ChatModel`. This is the payoff of the Adapter lesson: the adapters give you one interface, and the decorators operate on that interface without knowing the vendor.

```python
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ChatRequest:
    prompt: str


@dataclass(frozen=True, slots=True)
class ChatReply:
    text: str
    output_tokens: int


class ModelUnavailable(Exception): ...


class ChatModel(Protocol):
    def generate(self, request: ChatRequest) -> ChatReply: ...


class RetryingModel:
    def __init__(self, inner: ChatModel, attempts: int = 3, backoff_s: float = 0.0) -> None:
        self._inner, self._attempts, self._backoff = inner, attempts, backoff_s

    def generate(self, request: ChatRequest) -> ChatReply:
        for attempt in range(1, self._attempts + 1):
            try:
                return self._inner.generate(request)
            except ModelUnavailable:
                if attempt == self._attempts:
                    raise
                time.sleep(self._backoff * attempt)
        raise AssertionError("unreachable")


class CachingModel:
    def __init__(self, inner: ChatModel) -> None:
        self._inner = inner
        self._cache: dict[str, ChatReply] = {}

    def generate(self, request: ChatRequest) -> ChatReply:
        hit = self._cache.get(request.prompt)
        if hit is None:
            hit = self._cache[request.prompt] = self._inner.generate(request)
        return hit


class MeteredModel:
    def __init__(self, inner: ChatModel) -> None:
        self._inner = inner
        self.calls = 0
        self.tokens = 0

    def generate(self, request: ChatRequest) -> ChatReply:
        self.calls += 1
        reply = self._inner.generate(request)
        self.tokens += reply.output_tokens
        return reply


class FlakyModel:
    """Fails twice, then answers. Counts real vendor calls."""
    def __init__(self) -> None:
        self.vendor_calls = 0

    def generate(self, request: ChatRequest) -> ChatReply:
        self.vendor_calls += 1
        if self.vendor_calls <= 2:
            raise ModelUnavailable("503")
        return ChatReply(f"answer to {request.prompt}", output_tokens=4)


base = FlakyModel()
metered = MeteredModel(CachingModel(RetryingModel(base)))   # metrics -> cache -> retry -> vendor
req = ChatRequest("what is a flyweight?")
print(metered.generate(req).text)
print(metered.generate(req).text)
print(metered.calls, metered.tokens, base.vendor_calls)
```

```text
answer to what is a flyweight?
answer to what is a flyweight?
2 8 3
```

Read the last line: two calls served, eight tokens **served**, three real vendor attempts (two failures and one success; the second call was a cache hit). **Order is semantics.** With `MeteredModel` outermost it counts what clients received, 8 tokens. Move it inside the cache and it counts only what you were billed for, 4. Put `RetryingModel` outside `CachingModel` and a cache hit still goes through the retry loop for no reason. Decorator stacks are built from the inside out; draw them as a stack when you explain a design.

### The decorator base class

When the interface has several methods, repeating pass-throughs in every layer is noise and a source of bugs when the interface grows. Write one base decorator that delegates everything, and let concrete decorators override only what they change. This is the shape in the Scaler file-storage and REST exercises (`BaseFileDecorator`, `BaseApiDecorator`).

```python
import zlib
from abc import ABC, abstractmethod


class FileStorage(ABC):
    @abstractmethod
    def store(self, name: str, data: bytes) -> None: ...
    @abstractmethod
    def retrieve(self, name: str) -> bytes: ...


class MemoryStorage(FileStorage):
    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}
    def store(self, name, data): self.blobs[name] = data
    def retrieve(self, name): return self.blobs[name]


class StorageDecorator(FileStorage):
    def __init__(self, inner: FileStorage) -> None:
        self._inner = inner
    def store(self, name, data): self._inner.store(name, data)
    def retrieve(self, name): return self._inner.retrieve(name)


class VirusScanned(StorageDecorator):
    def store(self, name, data):
        if b"EICAR" in data:
            raise ValueError(f"{name} rejected by scanner")
        super().store(name, data)             # retrieve is inherited untouched


class Compressed(StorageDecorator):
    def store(self, name, data): super().store(name, zlib.compress(data))
    def retrieve(self, name): return zlib.decompress(super().retrieve(name))


raw = MemoryStorage()
storage = VirusScanned(Compressed(raw))       # scan plaintext, then compress, then persist
storage.store("a.txt", b"hello " * 100)
print(len(raw.blobs["a.txt"]) < 600, storage.retrieve("a.txt")[:11])
try:
    storage.store("bad.txt", b"xxEICARxx")
except ValueError as e:
    print(e)
print("bad.txt" in raw.blobs)
```

```text
True b'hello hello'
bad.txt rejected by scanner
False
```

The scanner runs on plaintext because it wraps the compressor. Reverse the layers and it would scan compressed bytes and miss the signature. Likewise, encryption belongs after compression, since encrypted data does not compress.

### Pattern decorator versus Python's `@decorator`

They share the idea (wrap, delegate, same call shape) but differ in what they wrap. The structural pattern wraps an **object** at runtime and can hold state per instance; it suits multi-method interfaces. A function decorator wraps a **callable** at definition time and suits cross-cutting behaviour on a single entry point.

```python
import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(attempts: int = 3, on: tuple[type[BaseException], ...] = (ConnectionError,)):
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except on:
                    if attempt == attempts:
                        raise
            raise AssertionError("unreachable")
        return wrapper
    return decorate
```

Two production traps. First, omit `functools.wraps` and you lose `__name__`, `__doc__` and the signature, which breaks introspection tools and FastAPI dependency analysis. Second, wrapping an `async def` with a sync wrapper compiles and runs, but calling it returns a coroutine immediately: the `try` sees nothing, the retry never triggers, and `asyncio.iscoroutinefunction` on the result is `False`. Write a separate `async` wrapper.

### Flyweight: share the intrinsic, own the extrinsic

When a program holds millions of similar small objects, split each into **intrinsic state** (identical across many objects, immutable, shareable) and **extrinsic state** (varies per occurrence, passed in or stored by the owner). Intrinsic parts live in a pool behind a factory that returns the existing instance for the same key. In a text renderer the glyph style (character, font, size) is intrinsic; the position is extrinsic. In a chess service the profile (name, email, photo) is intrinsic across the games a user plays, while colour and streak belong to each game. The same split fits token objects in an LLM tokenizer or per-chunk metadata that repeats the same source document.

```python
import sys
from dataclasses import dataclass
from weakref import WeakValueDictionary


@dataclass(frozen=True, slots=True, weakref_slot=True)    # weakref_slot needs 3.11+
class Glyph:                       # intrinsic: shared and immutable
    char: str
    font: str
    size: int


class GlyphFactory:
    def __init__(self) -> None:
        self._pool: WeakValueDictionary[tuple[str, str, int], Glyph] = WeakValueDictionary()

    def get(self, char: str, font: str = "Inter", size: int = 12) -> Glyph:
        key = (char, font, size)
        glyph = self._pool.get(key)
        if glyph is None:
            glyph = self._pool[key] = Glyph(*key)
        return glyph

    def __len__(self) -> int:
        return len(self._pool)


@dataclass(slots=True)
class Placed:                      # extrinsic: position, owned by the occurrence
    glyph: Glyph
    x: int
    y: int


factory = GlyphFactory()
doc = [Placed(factory.get(ch), x=i * 7, y=0) for i, ch in enumerate("hello world " * 1000)]
print(len(doc), len(factory))
print(doc[0].glyph is doc[12].glyph)
del doc
print(len(factory))

print(sys.intern("system_prompt_v3") is sys.intern("system_" + "prompt_v3"))
a, b = 256, 256
c, d = int("1000"), int("1000")
print(a is b, c is d)
```

```text
12000 8
True
0
True
True False
```

Twelve thousand placed glyphs share eight `Glyph` objects. The factory is the pooled-registry idea from the Prototype and Registry lesson, with a twist: a `WeakValueDictionary` lets unused flyweights be collected, which is why the pool is empty after `del doc`. With `__slots__` a weak reference needs a `__weakref__` slot; without `weakref_slot=True` (or an explicit `__weakref__` slot) `weakref.ref(...)` raises `TypeError`.

The last lines are CPython's own flyweights: `sys.intern` pools strings, and small integers (`-5` through `256`) are cached, while `int("1000")` creates new objects. That small-int cache is an implementation detail, never something to rely on with `is`.

`__slots__` is an orthogonal saving. On a CPython 3.13 run, 100,000 three-field instances traced about 104 bytes each as plain classes versus about 64 with `__slots__`. Useful, but the big win is not creating the duplicates at all, and when objects are numeric the real answer is often a NumPy array or `array.array`, not an object pool.

> **Pitfall:** Flyweights must be immutable. If one holder mutates a shared intrinsic object, every holder sees the change. Use `frozen=True`, and keep the registry's get-or-create under a lock when threads can race, otherwise two threads can create duplicates for the same key.

### Where the wrappers sit

| Pattern | Wraps | Interface | Intent |
|---|---|---|---|
| Adapter | One object | Changes it to a target | Make incompatible things fit |
| Facade | A subsystem | New, simpler | Hide coordination |
| Decorator | One object | Same | Add behaviour, stackable |
| Proxy | One object | Same | Control access (lazy, remote, auth) |

> **Interview tip:** Decorator versus Proxy is the favourite trap, since the code is nearly identical. The tell is intent and who builds it: a decorator is composed by the client to add features; a proxy is usually created by infrastructure to stand in for the real object.

## Practical Backend Scenario

Your LLM gateway serves several tenants. Tenant A wants caching, tenant B forbids it for data-residency reasons, and tenant C needs a stricter retry budget and per-request token metering for billing. If those variations are flags inside one `OpenAIClient` class, every new combination is another branch. With decorators you assemble the stack per tenant at startup (`Metered(Retrying(adapter))` for C, the bare adapter for B) and unit test each layer alone. Separately, the gateway tokenizes prompts into millions of `(token, style)` records for audit logs; sharing the intrinsic part through a factory and storing only per-occurrence offsets cuts the memory profile enough to run on the smaller instance type.

## Practice Loop

1. Type out the three model decorators and run the stack. Reorder the layers four ways and write down how `calls`, `tokens` and `vendor_calls` change each time.
2. Add a `TimeoutModel` decorator that raises `ModelUnavailable` when the inner call exceeds a deadline. Decide where it sits relative to retry, and defend the choice.
3. Write `@retry` as a function decorator and prove that `functools.wraps` preserved `__name__`. Then wrap an `async def` with it and observe what goes wrong. Write the async version.
4. Build the `StorageDecorator` stack. Add an `Encrypted` layer (use a trivial XOR stand-in) and put it in the wrong place on purpose to see why order matters for compression.
5. Implement the glyph flyweight, then remove `frozen=True` and write a test that shows one holder corrupting another.
6. Measure memory for 100,000 plain objects versus `__slots__` versus shared flyweights with `tracemalloc` and record the three numbers.

## Evidence of Understanding

- I can explain why decorators implement the same interface as the component and what that buys.
- I can predict how a change in stacking order changes metrics, cache behaviour and security checks.
- I can state two differences between the object decorator pattern and Python's `@decorator`, including the async trap.
- I can split a class into intrinsic and extrinsic state and justify each field.
- I can explain why flyweights must be immutable and how a weak-value registry avoids leaks.
- I can say when `__slots__`, an array, or interning is a better fix than a flyweight pool.

## Interview Questions to Rehearse

### Q: How do you add retries, caching and metrics to an LLM client without touching the client?

Wrap it. Each concern becomes a decorator that implements the same `ChatModel` interface and delegates to an inner model, then the stack is assembled at startup. Order is deliberate: metrics outermost to count served traffic or innermost to count billed traffic, cache outside retry so hits skip the retry loop, timeout inside retry so each attempt has its own deadline. Each layer is independently testable with a fake inner model.

### Q: How is the Decorator pattern different from a Python function decorator?

Both wrap and delegate, but the pattern wraps an object that satisfies an interface at runtime, may carry per-instance state, and can be composed per use. A function decorator wraps a callable once at definition time. Function decorators need `functools.wraps`, and sync wrappers silently mishandle coroutines, so async needs its own wrapper.

### Q: Decorator versus Proxy?

Structurally similar: both implement the component's interface and hold a reference to it. A decorator adds responsibilities and is composed freely by the caller. A proxy controls access to the real object (lazy loading, remote call, authorization) and usually decides whether and when to create or call it.

### Q: When is Flyweight worth it, and when is it a distraction in Python?

When there are very many objects with substantial shared immutable state, measurable in `tracemalloc`. It is a distraction when the objects are small numeric records (use arrays), when only the per-instance overhead matters (use `__slots__`), or when sharing adds lookup cost without moving the memory profile. I would measure first.

### Q: What breaks a flyweight in production?

Mutating shared state, an unsynchronized get-or-create that makes duplicate instances, and a strong-reference pool that never frees entries. Fixes: immutable intrinsic objects, a lock around creation, and a `WeakValueDictionary` or bounded cache for the pool.

## Common Pitfalls

- Stacking order chosen by accident: scanning after compression, retrying around a cache, metering what was never billed.
- Forgetting `functools.wraps`, or applying a sync wrapper to an `async def`.
- Decorators that reach into the inner object's private attributes instead of delegating through the interface.
- Giving the base decorator `__getattr__` delegation and then losing type checking and discoverability.
- Flyweight objects that are mutable, or intrinsic state that secretly varies (for example a per-game field in the shared profile).
- Treating `is` on small ints or strings as a reliable equality test because interning made it work once.
- Pool growth: an unbounded flyweight dictionary is a memory leak with extra steps.

## Suggested Extension

Build a configurable stack factory that reads a per-tenant YAML or dict (`["metered", "cache", "retry"]`) and assembles the decorators in order around any `ChatModel`, rejecting orders that violate a rule you define (for example, metering inside caching is allowed, caching inside retry is not). Add a test that asserts the assembled stack's types from outermost to innermost.
