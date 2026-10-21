# Magic Methods and the Python Data Model

Python's built-in syntax is a thin layer over special methods: `len(x)`, `x in y`, `with`, `==`, `x[0]`, `x(...)` and even attribute access all dispatch to dunder methods on the object's type. If you can read the data model, you can build value objects that behave inside sets and dicts, containers that work with `for` and slicing, and resources that clean up reliably. Most of the subtle production bugs in this area, from unhashable value objects to infinite recursion in `__getattr__`, are breaches of contracts that interviewers like to probe.

## Concepts Covered

### Dunders are looked up on the type

When you write `len(obj)`, CPython calls `type(obj).__len__(obj)`, skipping the instance dictionary. That is why assigning `c.__len__ = lambda: 5` on an instance does not make `len(c)` work (it raises `TypeError: object of type 'C' has no len()`), and why special methods can be implemented in C without a per-instance cost. The practical rule: define dunders in the class body, never patch them onto instances, and remember that a mock must be installed on the class.

### Representations: `__repr__`, `__str__`, `__format__`

`__repr__` is for developers and logs: it should be unambiguous, ideally something you could paste to rebuild the object. `__str__` is for end users and falls back to `__repr__` when absent, but not the other way round. Containers print the `repr` of their elements, so a good `__repr__` makes logs readable. `__format__` powers f-string format specs such as `f"{price:.2f}"`.

### Equality, ordering and the hash contract

Equality must be consistent with hashing: if `a == b` then `hash(a) == hash(b)`. The default `object` implementation uses identity for both. When a class defines `__eq__` and not `__hash__`, Python sets `__hash__ = None` so the class becomes unhashable, because the inherited identity hash would break the contract. Return `NotImplemented` (not `False`, not an exception) for operands you do not understand, so Python can try the reflected operation and finally fall back to identity.

```python
class Money:
    __slots__ = ("amount", "currency")          # amount in paise

    def __init__(self, amount: int, currency: str) -> None:
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "currency", currency)

    def __setattr__(self, name, value):
        raise AttributeError("Money is immutable")

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount / 100:.2f} {self.currency}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __radd__(self, other: object):           # lets sum() start from 0
        return self if other == 0 else NotImplemented

m = Money(1050, "INR")
print(repr(m), "|", m, "|", sum([m, m]), "|", {m, Money(1050, "INR")} == {m}, "|", m == 5)
```

```text
Money(1050, 'INR') | 10.50 INR | 21.00 INR | True | False
```

The hash must be computed from the **same immutable fields** as equality. If a field used in `__hash__` mutates after the object is in a set, the object sits in the wrong bucket and is effectively lost:

```python
class Bad:
    def __init__(self, k): self.k = k
    def __eq__(self, o): return self.k == o.k
    def __hash__(self): return hash(self.k)

b = Bad(1); s = {b}; b.k = 2
print(b in s, Bad(2) in s, len(s))     # False False 1
```

The set still contains the object, but neither lookup can find it. Related facts worth knowing: `1 == 1.0 == True` and all three hash alike, which is why `{1: "a"}.get(1.0)` returns `"a"`, and `@dataclass(frozen=True)` generates a consistent `__eq__`/`__hash__` pair for you. Defining only `__lt__` gives you `sorted` and `min`, and `functools.total_ordering` fills in the rest from `__eq__` plus one ordering method.

### Containers: `__len__`, `__iter__`, `__getitem__`, `__contains__`, `__bool__`

Each protocol is independent, and Python has fallbacks that matter in practice. Truthiness uses `__bool__`, then `__len__`, so an "empty" collection is falsy. `in` uses `__contains__`, then iterates via `__iter__`, then falls back to the legacy `__getitem__` with integers from 0 until `IndexError`. Delegating `__getitem__` to an internal list passes slice objects through, so slicing works without extra code, but be aware that `obj[:2]` then returns whatever the list returns, usually a plain list rather than your container type.

```python
class TripLog:
    def __init__(self, trips):
        self._trips = list(trips)
    def __len__(self): return len(self._trips)
    def __iter__(self): return iter(self._trips)
    def __getitem__(self, i): return self._trips[i]
    def __contains__(self, t): return t in self._trips

log = TripLog(["a", "b", "c"])
print(len(log), log[:2], log[-1], "b" in log, bool(TripLog([])), list(log))

class OnlyGetitem:
    def __getitem__(self, i):
        if i >= 3:
            raise IndexError
        return i * 10

print(list(OnlyGetitem()), 20 in OnlyGetitem())
```

```text
3 ['a', 'b'] c True False ['a', 'b', 'c']
[0, 10, 20] True
```

For anything non-trivial, subclass an ABC from `collections.abc` (`Sequence`, `Mapping`) so you inherit consistent mixin methods instead of hand-writing each dunder. Make `__iter__` return a fresh iterator each time, otherwise a second loop over the same object silently yields nothing.

### Context managers: `__enter__` and `__exit__`

`with` guarantees `__exit__` runs, on success or on exception. It receives the exception type, value and traceback (or three `None`s), and its **return value decides** whether the exception is suppressed: a truthy return swallows it, anything else lets it propagate after cleanup. Swallow only the exact exception you can handle; returning `True` unconditionally hides bugs. If `__exit__` itself raises, the new exception replaces the original (chained via `__context__`).

```python
from contextlib import contextmanager

class Tx:
    def __init__(self, swallow_keyerror=False):
        self.swallow = swallow_keyerror
    def __enter__(self):
        print("begin"); return self
    def __exit__(self, et, ev, tb):
        print("exit", et.__name__ if et else None)
        return et is KeyError and self.swallow

with Tx(True):
    raise KeyError("x")                 # begin / exit KeyError, then execution continues
try:
    with Tx():
        raise ValueError("boom")        # begin / exit ValueError, then propagates
except ValueError as e:
    print("propagated", e)

@contextmanager
def tx():
    print("begin")
    try:
        yield
    except KeyError:
        print("rollback")               # catching here suppresses the exception
    else:
        print("commit")

with tx(): raise KeyError
with tx(): pass
```

`@contextmanager` is the idiomatic shortcut: code before `yield` is `__enter__`, and the `try/except/else/finally` around it is `__exit__`. Use a class when the manager is reusable, holds state, or must be re-entrant.

### Attribute access: `__getattr__` versus `__getattribute__`

`__getattribute__` runs on **every** attribute read. `__getattr__` runs only as a fallback after normal lookup (instance dict, class MRO, descriptors) raises `AttributeError`. Use `__getattr__` for proxies and lazy config; reserve `__getattribute__` for rare interception and always delegate with `object.__getattribute__(self, name)`, because touching `self.anything` inside it recurses forever. The classic production bug is a `__getattr__` that reads `self._data` before `_data` exists, which happens when `copy.copy` or `pickle` build a blank instance: `_data` is missing, `__getattr__("_data")` calls itself, and you get `RecursionError`. Raise `AttributeError` for private and dunder names.

```python
class Settings:
    def __init__(self, data):
        self._data = dict(data)
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)          # protects copy/pickle and hasattr probes
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name) from None

s = Settings({"timeout": 30})
print(s.timeout, getattr(s, "missing", "default"), hasattr(s, "nope"))   # 30 default False
```

Always raise `AttributeError` (never `KeyError`) from these methods, since `getattr(x, name, default)` and `hasattr` depend on it.

### Callable objects and when not to add a dunder

`__call__` turns an object into a function with memory. `SurgePricing(multiplier, base_fare)` called as `surge(4.2)` configures once and calls many times, and works anywhere a callable is accepted, such as `map` or a FastAPI dependency. The risk is that readers assume a plain function and miss hidden state. The one rule for all dunders: add one only when a real caller needs the object to speak Python's existing vocabulary (`len`, `in`, `==`, `with`); do not wire up buttons nobody presses or give surprising meaning to familiar syntax.

## Practical Backend Scenario

An LLM gateway caches model responses keyed by a `PromptKey(model, temperature, messages)` object. A developer adds `__eq__` that compares all three fields and a `__hash__` over the same, and everything works. Weeks later, a middleware appends a system message to `messages` (a list) after the key is already in the cache dict. Lookups start missing; hit rate collapses; the cache grows without bound because duplicate keys are now both present. The fix is a frozen key: convert `messages` to a tuple of tuples at construction, use `@dataclass(frozen=True)`, and add a test that hashes a key, mutates through every public path, and asserts the hash is unchanged.

## Practice Loop

1. Implement `Trip` with `__repr__` and no `__str__`; compare `print(trip)`, `repr(trip)`, `f"{trip}"` and a list containing it.
2. Add `__eq__` to `Driver` by `driver_id`, show `Driver.__hash__` is `None`, then add a matching `__hash__` and put drivers in a set.
3. Demonstrate the lost-key bug by mutating a hashed field after insertion, then fix it with `@dataclass(frozen=True)`.
4. Build `TripLog` with `__len__`, `__iter__`, `__getitem__`, `__contains__`; test slicing, truthiness and a second `for` loop over it.
5. Write `TripTimer` as a class and again with `@contextmanager`; make `__exit__` swallow only `TripCancelledError`.
6. Write a `Settings` proxy with `__getattr__`, then break it with `copy.copy`, and fix the recursion.
7. Make `SurgePricing` callable and pass it to `map`.

## Evidence of Understanding

- You can state the hash/equality contract and explain what breaks if either side mutates.
- You can explain why `__hash__` becomes `None` and when `NotImplemented` is the right return.
- You can predict `in`, `bool`, `for` and slicing behaviour for a class given only the dunders it defines.
- You can say how the return value of `__exit__` changes control flow.
- You can explain the difference between `__getattr__` and `__getattribute__` and the recursion trap in each.

## Interview Questions to Rehearse

### Q: What is the contract between `__eq__` and `__hash__`, and what does Python do if you break it?
Equal objects must have equal hashes, and the hash must stay stable while the object is in a hashed collection. Python enforces only the easy half: defining `__eq__` without `__hash__` sets `__hash__` to `None`. It cannot stop you hashing mutable fields, which then leaves objects unreachable in sets and dict keys.

### Q: Why return `NotImplemented` from `__eq__` instead of `False`?
It tells Python "I do not know this type", so it tries the reflected `other.__eq__(self)`, letting the other class decide. Returning `False` blocks that and breaks symmetric comparisons with subclasses or foreign types. With both sides returning `NotImplemented`, `==` falls back to identity.

### Q: What does `__exit__` returning `True` do, and what are the risks?
It suppresses the in-flight exception and execution continues after the `with` block. Returning `False` or `None` re-raises after cleanup. The risk is swallowing unrelated errors, so check the type, log, and keep suppression narrow.

### Q: `__getattr__` versus `__getattribute__`?
`__getattribute__` runs for every access; `__getattr__` runs only after normal lookup fails. Inside `__getattribute__` you must call `object.__getattribute__` to avoid recursion; inside `__getattr__` you must not touch attributes that may be missing, which is what breaks `copy` and `pickle`. Both should raise `AttributeError` for unknown names.

### Q: How does Python decide whether an object is truthy, and how does `x in obj` work?
Truthiness: `__bool__`, then `__len__`, else true. Membership: `__contains__`, then iteration with `__iter__`, then the old `__getitem__` protocol with integers until `IndexError`. This is why a class with only `__getitem__` is iterable.

### Q: When would you use `__call__`?
When an object is configured once and invoked many times, such as a pricing policy, validator or callback, and it needs state. Prefer a closure for tiny cases and a plain function when there is no state; avoid it when it hides side effects from readers.

## Common Pitfalls

- Defining `__eq__` and forgetting `__hash__`, then being surprised by `TypeError: unhashable type`.
- Hashing a mutable field (a list, a dict, a counter) and losing objects in a set.
- Raising an exception or returning `False` from `__eq__` for foreign types instead of `NotImplemented`.
- Patching a dunder onto an instance and expecting `len()` or `with` to see it.
- Returning `True` from `__exit__` regardless of the exception type.
- A `__getattr__` that accesses `self.x` for an `x` that may not exist yet, causing `RecursionError` in `copy` or `pickle`.
- Making `__iter__` return `self` without resetting, so a container can be iterated only once.
- Implementing `__len__` on a domain object and accidentally making an empty instance falsy in `if obj:` checks.

## Suggested Extension

Write a small `FrozenKey` base class for cache keys that normalises lists and dicts to tuples at construction, generates `__eq__` and `__hash__` from declared fields, and refuses attribute assignment. Add a property-based test (Hypothesis, if available) asserting `a == b` implies `hash(a) == hash(b)` for random inputs.
