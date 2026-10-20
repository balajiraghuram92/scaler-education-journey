# The CPython Object Model and Memory Management

Most Python memory incidents in production are not exotic: a cache that quietly pins every request object, a default argument shared across all callers, a prefork worker pool whose memory climbs as pages are copied-on-write, or an object graph that only a cycle collector can free. Interviewers use this topic to separate engineers who treat Python as "a language with a garbage collector" from those who can say exactly when an object dies and what it costs. This lesson builds the mental model of what a Python object is in CPython, how it is freed, and how to measure it honestly.

## Concepts Covered

### Everything is a PyObject

In CPython every value, including an int, a function, a class and `None`, is a heap-allocated C struct that begins with a `PyObject` header. The header holds two fields: a reference count (`ob_refcnt`) and a pointer to the type object (`ob_type`). Variable-size objects such as `list`, `tuple` and `bytes` use a `PyVarObject` header that adds `ob_size`. Names are not boxes holding values; a name is an entry in a namespace (a dict, a fast-local slot, or a cell) that points at an object. Assignment binds a name, it never copies.

Three questions are often conflated:

- `id(x)` is an integer that is unique among simultaneously live objects. In CPython it happens to be the memory address, but that is an implementation detail and it is reused after the object dies.
- `a is b` compares identities, that is, whether both names reference the same object.
- `a == b` calls `type(a).__eq__`, which is whatever the class defines.

Use `is` only for singletons (`None`, `True`, sentinels you create with `object()`). Never use it to compare numbers or strings: which equal values happen to be the same object is a CPython optimization, not a language guarantee.

> **Interview tip:** If asked "why does `a is b` give True for 256 but False for 257?", the senior answer is that the result is an implementation artifact (small-int cache, constant folding within a code object) and that correct code never depends on it.

### Mutability and the aliasing traps

Because names are references, mutating a shared mutable object is visible through every alias. Three traps account for most real bugs: default arguments are evaluated once at function definition time and stored in `__defaults__`; `[x] * n` repeats the same reference `n` times; and `+=` on a list mutates in place while `+` builds a new object.

```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

print(add_tag("a"), add_tag("b"))
print(add_tag.__defaults__)

grid = [[0] * 3] * 2           # two references to one inner list
grid[0][0] = 9
print(grid)

grid_ok = [[0] * 3 for _ in range(2)]
grid_ok[0][0] = 9
print(grid_ok)
```

```text
['a', 'b'] ['a', 'b']
(['a', 'b'],)
[[9, 0, 0], [9, 0, 0]]
[[9, 0, 0], [0, 0, 0]]
```

Note that the first line prints the same list twice, because both calls returned the one object stored in `__defaults__`. The idiom for a fresh default is `tags: list[str] | None = None` followed by `tags = [] if tags is None else tags`. The same family of bug appears in `dict.fromkeys(keys, [])` and in dataclass fields, where `field(default_factory=list)` is required (a bare `[]` default raises `ValueError`, which exists precisely to stop this trap).

A related surprise: `t = ([1], 2); t[0] += [9]` raises `TypeError` yet leaves `t == ([1, 9], 2)`. The in-place `extend` succeeds first, then the rebind to the tuple slot fails.

### Reference counting and `sys.getrefcount`

CPython frees most objects deterministically: when `ob_refcnt` drops to zero the object is deallocated immediately, its `__del__` runs, and its referents are decremented in turn. This is why `with` blocks are about resource timing guarantees rather than memory, and why code that "works" in CPython by relying on refcounting can leak file handles on PyPy.

```python
import sys

x = object()
print(sys.getrefcount(x))   # the argument itself adds one temporary reference
y = x
print(sys.getrefcount(x))
del y
print(sys.getrefcount(x))
print(sys.getrefcount(None) > 1000, sys.getrefcount(1))
```

```text
2
3
2
True 4294967295
```

The last line shows a 3.12+ feature: PEP 683 made objects such as `None`, small ints and interned strings **immortal**, with a sentinel refcount that never changes. This avoids useless writes to shared pages (relevant for fork-based servers) and removes contention on common objects. The free-threaded 3.13t build (PEP 703) goes further, using biased reference counting so the owning thread updates the count without atomics.

Refcounting's weakness is cycles. If `a.peer = b` and `b.peer = a`, deleting both names leaves each with a count of one forever.

### The cyclic garbage collector and its generations

The `gc` module's collector exists only to find unreachable cycles among **container** objects (those that can reference others: lists, dicts, instances, closures). Ints and strings are never tracked. Tracked objects are placed in generations; young objects are scanned often and survivors are promoted to older generations, which are scanned rarely. `gc.get_threshold()` returns the allocation thresholds that trigger a collection (on 3.13 it printed `(2000, 10, 10)`; older versions used 700 for the first value, and the collector's tuning has changed between releases, so always check the "What's New" notes for your target version).

```python
import gc, weakref

class Node:
    def __init__(self):
        self.peer = None

gc.collect()
gc.disable()
n1, n2 = Node(), Node()
n1.peer, n2.peer = n2, n1
probe = weakref.ref(n1)
del n1, n2
print(probe() is not None)      # cycle keeps both alive
print(gc.collect() >= 2)        # the collector finds the cycle
print(probe())
gc.enable()
```

```text
True
True
None
```

Since PEP 442 (3.4), objects with `__del__` inside a cycle are collectable, and a finalizer runs at most once. Even so, prefer `weakref.finalize` or context managers for cleanup, because `__del__` timing is hard to reason about and it can resurrect the object.

> **Production note:** Gunicorn-style prefork servers load the app in a parent process, then fork. Copy-on-write only helps while pages stay clean, but both refcount updates and GC traversal write to objects. Calling `gc.freeze()` in the parent before forking moves everything currently tracked into a permanent generation that the collector ignores, which reduces page dirtying in workers. Immortal objects help for singletons only; ordinary objects still have their refcounts written.

### Weak references

A weak reference does not increment the refcount, so it lets you observe or cache an object without keeping it alive. `weakref.ref` returns a callable that yields the object or `None`; `WeakValueDictionary` and `WeakKeyDictionary` drop entries automatically; `weakref.finalize` registers cleanup that fires when the object dies.

```python
import weakref

class Model: ...

m = Model()
cache = weakref.WeakValueDictionary()
cache["m"] = m
print(len(cache))
del m
print(len(cache))
```

```text
1
0
```

Instances need a `__weakref__` slot to be weakly referenceable. Plain classes have one; a class with `__slots__ = ("x",)` does not, and `weakref.ref(obj)` raises `TypeError: cannot create weak reference to 'A' object`. Add `"__weakref__"` to `__slots__` if you need it. Builtins like `list`, `dict` and `int` cannot be weakly referenced either.

### Interning and small-object caches

CPython keeps a cache of small ints (-5 to 256), interns identifier-like string literals, and folds constants at compile time. Strings built at runtime are generally new objects, and `sys.intern` explicitly returns the canonical copy.

```python
import sys

s1 = "".join(["py", "thon"])
s2 = "python"
print(s1 == s2, s1 is s2, sys.intern(s1) is sys.intern(s2))
```

```text
True False True
```

Interning is a legitimate optimization when you hold millions of repeated strings, such as field names or tenant IDs parsed from JSON, because dict lookups then short-circuit on identity. Treat it as a memory tool, never a correctness tool.

### `__slots__` and honest memory measurement

An ordinary instance stores attributes in a per-instance `__dict__` (3.11+ uses inline values and shared keys to make this cheaper, but the dict still materializes when you touch `__dict__`). Declaring `__slots__` replaces the dict with fixed descriptors, saving memory and blocking typos like `obj.colour = ...`, at the price of no dynamic attributes, no default class-level values for slotted names (`ValueError: 'a' in __slots__ conflicts with class variable`), and subclasses regaining a `__dict__` unless they declare their own `__slots__`.

```python
import sys, tracemalloc

class P:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

class S:
    __slots__ = ("a", "b", "c")
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

for cls in (P, S):
    tracemalloc.start()
    objs = [cls(i, i, i) for i in range(100_000)]
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(cls.__name__, current // 1024, "KiB")

print(sys.getsizeof([[1] * 1000]), sys.getsizeof([]))
```

```text
P 13276 KiB
S 9367 KiB
64 56
```

Exact numbers vary by version and platform, and the per-instance saving here includes shared int objects, so treat the ratio as indicative. The last line shows the caveat that matters most: `sys.getsizeof` is **shallow**. It reports the container's own bytes and ignores everything it references, so a list holding a 1000-element list reports 64 bytes. To size a real structure use `tracemalloc`, or walk the object graph yourself and track visited `id`s.

## Practical Backend Scenario

An LLM gateway service wraps each tenant in a `Session` object and decorates `Session.render_prompt` with `functools.lru_cache(maxsize=None)` to avoid re-rendering templates. After a week the pods are OOM-killed. The cause is that the cache lives on the class and its keys include `self`, so every `Session` ever created is pinned by a strong reference from the cache. Reference counting never reaches zero, and the cyclic GC cannot help because the objects are reachable. The fix is a per-instance cache (a dict on `self`), a module-level cache keyed by `tenant_id` strings, or a bounded `maxsize`. You diagnose it by taking two `tracemalloc` snapshots under load and diffing them, by checking `Session.render_prompt.cache_info().currsize`, and by using a `weakref.ref` probe in a test to prove sessions die when they should.

## Practice Loop

1. Reproduce the default-argument bug, print `func.__defaults__` after three calls, then fix it with the `None` sentinel and assert the defaults tuple stays unchanged.
2. Use `sys.getrefcount` on an object while you add it to a list, a dict and a closure, and explain every increment.
3. Build the two-node cycle with `gc.disable()`, confirm via a `weakref.ref` that it survives `del`, then free it with `gc.collect()` and read the return value.
4. Create a `lru_cache`-decorated method, show with a weakref probe that `del instance` does not free it, then change it to a per-instance cache and show that it does.
5. Compare the `tracemalloc` footprint of one million plain instances against slotted ones, and compare `sys.getsizeof` on a nested list with the traced total.
6. Print `gc.get_threshold()` and `gc.get_count()`, allocate containers in a loop, and watch the counts reset after a collection.

## Evidence of Understanding

- I can explain why `[[0] * 3] * 2` aliases rows while a comprehension does not, and why default arguments are shared.
- I can state precisely when an object is freed by refcounting and when only the cyclic collector can free it.
- I can say what `gc.freeze()`, immortal objects and `gc.collect()` do, and when each matters for a forked server.
- I can explain why `sys.getsizeof` under-reports, and measure a structure correctly with `tracemalloc`.
- I can list the costs of `__slots__` (no `__dict__`, no `__weakref__` unless declared, inheritance gotchas) and decide when the saving is worth it.
- I can find an `lru_cache`-on-method leak and fix it without changing the public API.

## Interview Questions to Rehearse

### Q: How does CPython manage memory, and why is there a garbage collector if there is reference counting?

Reference counting frees most objects immediately and deterministically when the count reaches zero. It cannot free cycles, because every member keeps the others' counts above zero. The generational cyclic collector periodically traverses tracked container objects, subtracts internal references, and frees the groups left with no external reference. Objects are young-to-old promoted so the frequent scans stay cheap. Atomic types such as ints and strings cannot form cycles and are not tracked.

### Q: What is the difference between `is` and `==`, and why can `is` seem to work on small ints?

`is` tests object identity; `==` calls `__eq__`. Small ints (-5 to 256), interned strings and folded constants are shared by the CPython implementation, so `is` returns True by accident for them. Nothing in the language guarantees that, and it varies between versions and between modules versus the REPL. Use `is` for `None` and sentinels only.

### Q: Why did my service's memory grow even though I deleted the references?

Typical causes: a strong reference held in a cache, a closure or a bound method stored somewhere (including `lru_cache` keyed on `self`), a global registry, a traceback or exception stored for later (which holds frames), or a reference cycle with the collector disabled or lagging. I would take `tracemalloc` snapshots and compare them, use `gc.get_referrers` on a suspect, and put a `weakref` probe in a test.

### Q: When is `__slots__` worth using?

When you create very large numbers of small, uniform instances, such as parsed records or tokens, and attributes are fixed. It removes the per-instance dict, so memory and attribute access improve modestly, and it prevents accidental attributes. It costs flexibility: no dynamic attributes, careful inheritance, and `__weakref__` must be declared if needed. For plain data I would also consider `dataclass(slots=True)` (3.10+).

### Q: What does `gc.freeze()` do and why would a FastAPI deployment care?

It moves all currently tracked objects into a permanent generation that is never scanned. Calling it after warm-up in a preforking server's parent process reduces how often child processes touch (and so copy) the shared pages through GC traversal. It does not stop refcount writes, so it reduces rather than eliminates copy-on-write growth.

### Q: Why does `sys.getsizeof` not tell you how much memory an object uses?

It returns only the object's own allocation, including GC header overhead, and ignores referenced objects. A list of a million dicts reports the size of one pointer array. For total footprint use `tracemalloc` or a recursive walker with a visited set, and remember that shared objects (interned strings, small ints) would otherwise be counted many times.

## Common Pitfalls

- Mutable default arguments (`def f(x, acc=[])`) and mutable class attributes shared by all instances.
- `[[]] * n` and `dict.fromkeys(keys, [])` that alias one list everywhere.
- Using `is` to compare ints or strings, which appears to pass in tests and fails on other values or Python versions.
- `functools.lru_cache` or `cache` on instance methods, which pins `self` for the life of the process.
- Relying on `__del__` for resource release instead of context managers or `weakref.finalize`.
- Trusting `sys.getsizeof` for nested objects, or concluding "there is no leak" from RSS alone without comparing allocation snapshots.
- Subclassing a slotted class without declaring `__slots__`, silently getting a `__dict__` back.
- Disabling the GC in a long-running service without a plan for cycles.

## Suggested Extension

Write a `leak_probe` context manager that records `tracemalloc` snapshots on entry and exit, plus a `weakref` registry of objects you track, and reports (a) the top ten allocation growth sites and (b) any tracked objects still alive after the block. Use it in a pytest fixture to assert that handling 1,000 simulated requests leaves no `Session` objects alive.
