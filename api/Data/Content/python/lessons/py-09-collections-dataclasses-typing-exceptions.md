# Collections, Dataclasses, Type Hints and Exceptions

Most production Python is not clever algorithms; it is modelling data cleanly, choosing the right container, saying what a function accepts and returns, and failing in a way that operators and callers can act on. This lesson covers the four tools behind that: the `collections` module, `dataclasses` (and its alternatives), type hints that actually pay for themselves, and exception design. Interviewers use them to see whether your code reads like a senior engineer's: no mutable-default bugs, no bare `except`, no lost tracebacks.

## Concepts Covered

### The collections module: pick the structure that removes code

`Counter` is a dict subclass for tallies, with `most_common(n)`, arithmetic between counters, and a `0` result for missing keys (without inserting them). `defaultdict(factory)` calls the factory on a **missing key lookup and inserts the result**, so `groups[key].append(x)` needs no existence check, but a bare read like `d["zzz"]` also creates the key, which can surprise you in membership tests. `deque` gives O(1) appends and pops at both ends (a list is O(n) at the front) and `maxlen` turns it into a fixed-size sliding window.

```python
from collections import Counter, defaultdict, deque

words = "the quick the lazy the dog quick".split()
freq = Counter(words)
print(freq.most_common(2))          # [('the', 3), ('quick', 2)]
print(freq["missing"], len(freq))   # 0 4  (lookup does not insert)

groups: defaultdict[str, list[str]] = defaultdict(list)
for w in ["eat", "tea", "tan", "ate", "nat", "bat"]:
    groups["".join(sorted(w))].append(w)    # anagram key
print(list(groups.values()))        # [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]

window: deque[int] = deque(maxlen=3)        # last 3 latency samples
for sample in range(5):
    window.append(sample)
print(window)                       # deque([2, 3, 4], maxlen=3)
```

### Dataclasses: boilerplate removal with sharp edges

`@dataclass` generates `__init__`, `__repr__` and `__eq__` from annotated fields. The options that matter in production:

- `frozen=True` makes instances immutable (assignment raises `FrozenInstanceError`) and, with the default `eq=True`, generates `__hash__`, so value objects can be dict keys. A non-frozen dataclass with `eq=True` sets `__hash__` to `None` and is **unhashable**.
- `slots=True` (3.10+) uses `__slots__`: smaller instances, faster attribute access, no accidental new attributes, and no `__dict__`.
- `kw_only=True` (3.10+) forces keyword construction, which prevents positional mix-ups and solves the inheritance problem where a subclass field without a default follows a base field with one.
- `order=True` adds `<`, `<=`, `>`, `>=` comparing fields as a tuple.
- `field(default_factory=list)` is mandatory for mutable defaults: `books: list = []` raises `ValueError` at class creation, protecting you from the shared-default bug that plain classes allow.
- `field(init=False, repr=False, compare=False)` controls per-field behaviour; `InitVar` passes a value to `__post_init__` without storing it.
- `__post_init__` is the place for validation and derived fields. `dataclasses.replace(obj, **changes)` copies with changes, which is how you "modify" frozen objects.

```python
from dataclasses import dataclass, field, replace, FrozenInstanceError

@dataclass(frozen=True, slots=True, kw_only=True, order=True)
class Money:
    amount_minor: int
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount_minor < 0:
            raise ValueError("amount_minor must be >= 0")

m = Money(amount_minor=500)
print(m, m < Money(amount_minor=700))      # Money(amount_minor=500, currency='USD') True
print(replace(m, currency="EUR"))
try:
    m.amount_minor = 1
except FrozenInstanceError as e:
    print("FrozenInstanceError:", e)       # cannot assign to field 'amount_minor'

@dataclass
class PromptTemplate:
    text: str
    tags: list[str] = field(default_factory=list)   # a new list per instance
```

> **Pitfall:** `frozen=True` is shallow. A frozen dataclass holding a `list` field is still mutable through that list, and its hash will raise `TypeError` if the list is part of the hash.

### Choosing between NamedTuple, dataclass, TypedDict and Pydantic

| Tool | Runtime type | Mutable | Validates | Best for |
|---|---|---|---|---|
| `NamedTuple` | tuple subclass | No | No | Small immutable records, tuple unpacking, cheap and hashable |
| `@dataclass` | normal class | Optional (`frozen`) | Only what you write | Internal domain objects with behaviour |
| `TypedDict` | plain `dict` | Yes | No (type checker only) | Describing JSON-shaped dicts you already have |
| Pydantic `BaseModel` | model class | Optional | Yes, at runtime | Data crossing a trust boundary (HTTP, LLM output) |

`NamedTuple` and tuples unpack (`x, y = point`) and compare equal to plain tuples, which can hide bugs; dataclasses are distinct types. `TypedDict` instances are ordinary dicts at runtime, so nothing is checked unless a type checker or validator does it. Use dataclasses inside your domain and Pydantic at the edges.

### Type hints that pay for themselves

Type hints are not enforced at runtime. They are consumed by editors, `mypy` or `pyright`, and libraries like Pydantic and FastAPI. Spend them where they prevent real bugs:

- Public function signatures and return types, especially `X | None` so callers must handle absence.
- Containers: `list[str]`, `dict[str, int]`, `Mapping` and `Sequence` for read-only parameters, `Iterable` when you only loop.
- `Protocol` for duck-typed dependencies, `Literal["a", "b"]` for closed sets of strings, `Enum` or `StrEnum` for states, and `Final` for constants.
- Generics with the 3.12 syntax, `def first[T](items: Sequence[T]) -> T`, and `Self` for fluent return types.
- `TypedDict` with `NotRequired` for dict-shaped payloads you cannot convert yet.

Avoid annotating everything with `Any`, which switches checking off, and prefer narrowing (`if x is None: ...`) over `cast`. Run a type checker in CI, otherwise annotations rot.

```python
from collections.abc import Sequence
from enum import Enum
from typing import Literal, Protocol

class LoanStatus(Enum):
    ACTIVE = "active"
    RETURNED = "returned"

class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...

def first[T](items: Sequence[T]) -> T | None:
    return items[0] if items else None

def pick_model(tier: Literal["fast", "accurate"]) -> str:
    return "small" if tier == "fast" else "large"

print(LoanStatus.ACTIVE.value)   # active
```

### Exception design: hierarchy, chaining and cleanup

Build one **base exception per library or service** (`class AppError(Exception)`), then specific subclasses that carry data (`ProviderError(provider, status)`). Callers can catch the base for generic handling or the leaf for specific recovery, and domain exceptions replace booleans and `None` returns that hide *why* something failed. Catch the narrowest type you can handle, never a bare `except:` (it also traps `KeyboardInterrupt` and `SystemExit`), and avoid `except Exception: pass`, which hides bugs.

Block order is `try` (the risky call only), `except` (handle), `else` (runs only if no exception, keeps the `try` body minimal), `finally` (always runs, for cleanup). A `return` in `finally` silently swallows an in-flight exception, so avoid it.

**Chaining:** `raise NewError(...) from exc` sets `__cause__` and preserves the original traceback, so you can translate a low-level `ConnectionResetError` into a domain `ProviderError` without losing the root cause. Raising inside an `except` without `from` still records `__context__` implicitly ("During handling of the above exception..."). `from None` suppresses the context when it is noise. Since 3.11, `exc.add_note("...")` attaches extra context to an exception you re-raise.

```python
class AppError(Exception):
    """Base class for application errors."""

class ProviderError(AppError):
    def __init__(self, provider: str, status: int) -> None:
        super().__init__(f"{provider} returned {status}")
        self.provider, self.status = provider, status

def call_provider() -> None:
    raise ConnectionResetError("socket closed")

def fetch() -> None:
    try:
        call_provider()
    except OSError as exc:
        raise ProviderError("openai", 502) from exc

try:
    fetch()
except ProviderError as e:
    print(repr(e), "| cause:", repr(e.__cause__))
```

```text
ProviderError('openai returned 502') | cause: ConnectionResetError('socket closed')
```

**EAFP versus LBYL:** Python favours "easier to ask forgiveness than permission": try the operation and handle the exception, rather than checking first. It avoids races (a file can vanish between `exists()` and `open()`) and is often faster on the happy path. Use LBYL when the check is cheap and the failure is common or has side effects.

**Exception groups (3.11+):** when several independent tasks can fail at once (`asyncio.TaskGroup`, parallel provider calls), raise `ExceptionGroup("batch failed", [e1, e2])` and handle by type with `except*`, which can match several branches of the same group:

```python
def run_batch() -> None:
    errors: list[Exception] = []
    for n in (1, 2, 3):
        try:
            if n == 2:
                raise TimeoutError("t")
            if n == 3:
                raise ValueError("v")
        except Exception as exc:
            errors.append(exc)
    if errors:
        raise ExceptionGroup("batch failed", errors)

try:
    run_batch()
except* TimeoutError as eg:
    print("timeouts:", [str(e) for e in eg.exceptions])    # timeouts: ['t']
except* ValueError as eg:
    print("values:", [str(e) for e in eg.exceptions])      # values: ['v']
```

## Practical Backend Scenario

An LLM gateway receives JSON events from five providers and must (1) tally tokens per tenant, (2) keep the last 100 latency samples for a health endpoint, and (3) report failures. A `Counter` aggregates tokens, a `deque(maxlen=100)` holds the samples, and a frozen, slotted `Usage` dataclass represents each validated event (with `kw_only=True` so call sites are readable). Raw provider payloads are parsed at the edge by Pydantic, then converted to dataclasses internally. Provider failures are translated into `ProviderError(provider, status)` with `raise ... from exc`, so the retry layer can catch `ProviderError` with `status >= 500`, while a `ValidationError` is logged and skipped. When a fan-out call to five providers fails partially, an `ExceptionGroup` carries every failure to a single `except*` block that records metrics per exception type.

## Practice Loop

1. Count word frequencies in a paragraph with a plain dict, then `defaultdict(int)`, then `Counter`. Get the top three words with `most_common(3)`.
2. Implement `group_anagrams(strs)` with a `defaultdict(list)` keyed by `"".join(sorted(s))`. Handle `None` and an empty list by returning `[]`.
3. Define a `Member` dataclass with `books: list = []` and read the error. Fix it with `default_factory`. Then add `__post_init__` validation that rejects an empty name.
4. Make `Point(x, y)` frozen, show that assignment fails, use it as a dict key, then add a `list` field and observe the hash failure.
5. Write `AppError` and two subclasses. Translate a `KeyError` using `raise ... from exc`, then print `__cause__` and `__context__`. Repeat with `from None`.
6. Write `compare(x, y, key=None)` returning `-1`, `0` or `1`, and type it with a `TypeVar`.

## Evidence of Understanding

- I can pick between `Counter`, `defaultdict`, `deque` and `ChainMap` and justify each.
- I can explain why `x: list = []` fails in a dataclass and what `default_factory` does.
- I can state exactly what `frozen`, `slots`, `kw_only` and `order` change, and the hash rules.
- I can choose between `NamedTuple`, dataclass, `TypedDict` and Pydantic for a given boundary.
- I can design an exception hierarchy and explain `__cause__`, `__context__` and `from None`.

## Interview Questions to Rehearse

### Q: Why does a dataclass reject `books: list = []`, and what is the plain-class equivalent bug?

A default is evaluated once and shared by every instance, so one object's append would appear in all others. Dataclasses detect unhashable defaults (list, dict, set) and raise `ValueError`; `field(default_factory=list)` builds a fresh list per instance. In a plain class, `def __init__(self, books=[])` has exactly the shared-state bug, with no warning.

### Q: Do type hints make Python statically typed?

No. They are metadata; the interpreter does not enforce them. They pay off through a checker in CI (`mypy` or `pyright`), editor tooling, and runtime consumers like Pydantic and FastAPI. I annotate public signatures and boundaries first, and avoid `Any`.

### Q: What is exception chaining and when do you use `from None`?

`raise New from exc` sets `__cause__` so the original traceback is kept when translating a low-level error into a domain error. Raising inside an `except` without `from` records the original implicitly as `__context__`. I use `from None` only when the original is irrelevant noise, such as a `KeyError` from an internal lookup that I am turning into a clear validation error.

### Q: EAFP or LBYL?

Python prefers EAFP: attempt the operation and catch the specific exception. It avoids time-of-check races and double lookups. I use LBYL when the check is trivial and failure is the common case, or when the operation has side effects that I cannot undo.

## Common Pitfalls

- Mutable defaults in function signatures or classes (`def f(x=[])`).
- Assuming `frozen=True` makes nested containers immutable.
- Using `except:` or `except Exception: pass`, hiding real failures and interrupts.
- Raising a new exception inside `except` without `from`, hiding intent, or with `from None` when the cause matters.
- Returning from `finally`, which swallows exceptions.
- Reading a `defaultdict` key to test existence, which inserts it.

## Suggested Extension

Design the error model for a document-ingestion service: a base `IngestError`, retryable and non-retryable subclasses (a `retryable` attribute or two branches), and a function that processes a batch of documents concurrently and raises an `ExceptionGroup`. Write the `except*` handlers that retry the retryable group and dead-letter the rest, and type everything so that `mypy --strict` passes.
