# Advanced Typing and Static Analysis

Python's annotations are not enforced at runtime, which is exactly why a strict type checker in CI is the cheapest bug-finder a large codebase can have. At senior level, interviewers expect more than `list[str]`: generics with bounds, decorators that preserve signatures, structural interfaces, and a clear opinion on what strict mode buys you and where types stop (the network boundary, where Pydantic takes over). This lesson targets Python 3.12/3.13, where the generics syntax is much lighter.

## Concepts Covered

### Generics: `TypeVar`, bounds, constraints and PEP 695 syntax

A type variable ties types together across a signature: "whatever goes in comes out". Two ways to restrict one behave differently. A **bound** (`T: Sized`) accepts any subtype and keeps it, so passing a `list[int]` yields a `list[int]`. **Constraints** (`S: (str, bytes)`) permit exactly those types, and the checker solves the variable to one of them: a `str` subclass becomes plain `str`. Use a bound when you need "something with these methods", and constraints when the function body really needs different handling per type.

Python 3.12 (PEP 695) replaced the `TypeVar("T")` boilerplate with inline syntax. Type parameters belong to the function, class or alias; `type X = ...` creates a lazily evaluated alias, so recursive aliases need no quotes. Variance for PEP 695 classes is **inferred** by the checker, so you no longer pick `covariant=True` by hand. I ran the following on 3.13:

```python
from collections.abc import Hashable, Sequence


def first[T](xs: Sequence[T]) -> T:
    return xs[0]


class Repo[K: Hashable, V]:
    def __init__(self) -> None:
        self._rows: dict[K, V] = {}

    def put(self, key: K, value: V) -> None:
        self._rows[key] = value

    def get(self, key: K) -> V | None:
        return self._rows.get(key)


type Json = dict[str, Json] | list[Json] | str | int | float | bool | None

repo = Repo[str, int]()
repo.put("a", 1)
print(first.__type_params__, Repo.__type_params__, repo.get("a"))
```

```text
(T,) (K, V) 1
```

The type parameters are real runtime objects (`__type_params__`), but they are only used by checkers; `Repo[str, int]()` does not validate anything at runtime.

### `ParamSpec`: decorators that keep the signature

A decorator typed as `Callable[..., Any] -> Callable[..., Any]` erases the wrapped function's signature, so call sites lose all checking. `ParamSpec` (`**P`) captures the parameters of the function being wrapped and replays them on the wrapper, and `Concatenate` lets a decorator add or strip a leading parameter (a `request` or a DB session). For async functions use `Callable[P, Awaitable[R]]` and make the wrapper `async def`.

```python
import functools
from collections.abc import Callable


def retry[**P, R](attempts: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: ConnectionError | None = None
            for _ in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except ConnectionError as exc:
                    last = exc
            assert last is not None
            raise last

        return wrapper

    return decorate


calls = 0


@retry(attempts=3)
def fetch(url: str, *, timeout: float = 1.0) -> str:
    global calls
    calls += 1
    if calls < 3:
        raise ConnectionError("down")
    return f"ok:{url}"


print(fetch("http://x", timeout=2), calls, fetch.__name__)
```

```text
ok:http://x 3 fetch
```

A checker now knows `fetch("http://x", timeout="2")` is wrong, because `P` carries `(url: str, *, timeout: float = 1.0)`.

### `Protocol`, callback protocols and `overload`

A `Protocol` is structural typing: any class with the right methods is accepted, with no inheritance. Define the narrow interface the **consumer** needs (`class Closer(Protocol): def close(self) -> None`), not a mirror of the producer. A `__call__` protocol types callables with keyword-only or default arguments, which `Callable[...]` cannot express. `@runtime_checkable` enables `isinstance`, but only checks that the attribute **names** exist: I verified that an object whose `close` takes two required arguments still passes `isinstance(obj, Closer)`. Keep it for plugin discovery, not for validation.

`@overload` describes functions whose return type depends on the argument types. Write the signatures with `...` bodies, then one real implementation; the implementation is not visible to callers.

```python
from typing import Protocol, overload


class Scorer(Protocol):
    def __call__(self, text: str) -> float: ...


@overload
def parse(x: str) -> int: ...
@overload
def parse(x: bytes) -> float: ...
def parse(x: str | bytes) -> int | float:
    return int(x) if isinstance(x, str) else float(x)


def length_score(text: str) -> float:
    return len(text) / 100


scorer: Scorer = length_score
print(parse("3"), parse(b"2.5"), scorer("abc"))
```

```text
3 2.5 0.03
```

### `TypedDict`, `Literal`, `Final` and `Self`

`TypedDict` types JSON-shaped dictionaries (LLM tool-call payloads, API responses). At runtime it is a plain `dict`, so nothing is validated; use it for static shape, and Pydantic where you need validation. Mark individual keys with `Required[...]`, `NotRequired[...]`, and on 3.13 `ReadOnly[...]` (PEP 705). `Literal["system", "user", "assistant"]` restricts values; combine with `match` and `typing.assert_never` for **exhaustiveness**: if someone adds a new role and forgets a branch, the checker flags the `assert_never` call, and at runtime it raises `AssertionError`. `Final` forbids rebinding (and `@final` forbids subclassing or overriding), `@override` (3.12) turns a silent override typo into a checker error, and `Self` (3.11) types fluent builders and alternate constructors so subclasses get their own type back.

```python
from typing import Literal, NotRequired, Required, TypedDict, assert_never

Role = Literal["system", "user", "assistant"]


class Message(TypedDict):
    role: Required[Role]
    content: Required[str]
    name: NotRequired[str]


def label(role: Role) -> str:
    match role:
        case "system":
            return "S"
        case "user":
            return "U"
        case "assistant":
            return "A"
        case _ as unreachable:
            assert_never(unreachable)


msg: Message = {"role": "user", "content": "hi"}
print(label(msg["role"]), Message.__required_keys__ == {"role", "content"})
```

```text
U True
```

### Narrowing: `TypeGuard` versus `TypeIs`

A user-defined narrowing function returns `bool` at runtime and tells the checker what the argument is when it returns `True`. `TypeGuard[T]` narrows only the positive branch, and the negative branch is left unnarrowed. `TypeIs[T]` (PEP 742, in `typing` since 3.13) narrows **both** branches, so in the `else` the type is "the original minus `T`", but it requires that `T` be a subtype of the input type and that your check is truly exact. Prefer `TypeIs`; use `TypeGuard` when the narrowed type is not a subtype of the input (for example `list[object]` to `list[str]` as an unsound but convenient promise).

### Variance

`list[int]` is **not** a `list[float]`, because the callee could append a `float` and corrupt your list. `Sequence[float]` accepts it because `Sequence` is read-only and therefore covariant. Producers are covariant, consumers (callbacks, comparators) are contravariant, and anything both read and written is invariant. With PEP 695 syntax the checker infers this from how `T` is used in your class, so a `Box[T]` with only a getter is covariant automatically.

### Running mypy and pyright strictly

Configure in `pyproject.toml`: `[tool.mypy] strict = true` (bundles `disallow_untyped_defs`, `disallow_any_generics`, `warn_return_any`, `no_implicit_reexport`, `strict_equality` and more) or `[tool.pyright] typeCheckingMode = "strict"`. Adopt gradually: turn strict on globally, then add `[[tool.mypy.overrides]]` with relaxed flags for legacy modules and shrink the list over time. Enable `warn_unused_ignores` so stale `# type: ignore[code]` comments fail the build, and always use the error code. Use `reveal_type(x)` to see what the checker thinks, `cast` sparingly, and prefer `object` over `Any` at boundaries because `Any` silently disables checking.

> **Pitfall:** Types are erased at runtime. `Repo[str, int]()`, a `TypedDict` or a `cast` validates nothing. Data crossing a process boundary (HTTP, queue, LLM output) must be validated by something that runs, such as Pydantic, then flows into typed code.

## Practical Backend Scenario

Your LLM gateway has a `@with_retries` decorator typed as `Callable[..., Any]`. During a refactor someone renames `timeout` to `timeout_s` in `complete()`. Nothing fails in CI; a rarely used code path passes `timeout=` and raises `TypeError` in production at 3 a.m. Retyping the decorator with `ParamSpec`, moving the message payloads to `TypedDict` with `Literal` roles, and enabling strict mypy in CI turns that incident into a red build on the pull request.

## Practice Loop

1. Install `mypy` (and optionally `pyright`) in a scratch project, enable strict mode in `pyproject.toml`, and type the `Repo`, `retry` and `parse` examples.
2. Break the examples on purpose: call `fetch(url=1)`, call `parse(1)`, add a fourth `Role` without updating `label`, and write down each diagnostic.
3. Change `retry` to `Callable[..., Any]`, rerun, and observe which errors disappear.
4. Convert a `TypeVar` version of `Repo` to PEP 695 syntax, then try to pass `Repo[str, int]` where `Repo[str, float]` is expected and explain the result via variance.
5. Write a `TypeIs` function that narrows `str | int` to `str` and check what the `else` branch is for both `TypeIs` and `TypeGuard`.
6. Add the checker to CI as a required job with `warn_unused_ignores` on.

## Evidence of Understanding

- I can explain bound versus constrained `TypeVar` with an example where the results differ.
- I can write a `ParamSpec` decorator for both sync and async functions and say what `Concatenate` adds.
- I can explain why `list[int]` is not `list[float]` but `Sequence[int]` is acceptable as `Sequence[float]`.
- I can choose between `Protocol`, ABC and `TypedDict`, and state what `runtime_checkable` does and does not check.
- I can state what a strict checker catches and what only runtime validation catches.

## Interview Questions to Rehearse

### Q: What is the difference between a bound and constraints on a `TypeVar`?

A bound permits any subtype and preserves it in the result. Constraints permit exactly the listed types, and the variable resolves to the constraint, so a `str` subclass comes back as `str`. I use bounds for "has these methods" and constraints when the implementation branches on the concrete type.

### Q: Why does `Callable[..., Any]` make a decorator unsafe, and how do you fix it?

It erases the wrapped signature, so callers lose argument checking and return type information. `ParamSpec` and a return `TypeVar` let the wrapper present the exact same signature; `Concatenate` handles decorators that inject a first argument.

### Q: `Protocol` versus ABC?

A `Protocol` is structural: classes need no inheritance, which suits third-party types and small consumer-owned interfaces. An ABC is nominal and can share implementation and enforce registration. `runtime_checkable` only checks that names exist, not signatures, so I don't use it as validation.

### Q: `TypeGuard` versus `TypeIs`?

Both mark a boolean function as narrowing. `TypeGuard` narrows only when true; `TypeIs` narrows both branches and demands the narrowed type be a subtype of the input. Prefer `TypeIs` for accurate checks like `isinstance` wrappers.

### Q: Why can't I pass a `list[int]` to a function expecting `list[float]`?

Lists are mutable, so they are invariant: the callee could append a float to my list of ints. Accept `Sequence[float]` (covariant, read-only) instead, or make the function generic.

### Q: How do you roll out strict typing on a large untyped codebase?

Enable strict for new and touched modules, use per-module overrides for the legacy ones, set `warn_unused_ignores`, require error codes on ignores, fail CI on new errors only, and burn down the override list. I type the boundaries first (public service interfaces and Pydantic models) because that is where bugs enter.

## Common Pitfalls

- Believing annotations are enforced at runtime; `TypedDict`, `cast` and generic subscripts do not validate.
- Using `Any` where `object` or a `Protocol` would keep checking alive.
- Annotating `**kwargs: dict` (it means each value is a dict) instead of `**kwargs: int`.
- Mutable containers in public signatures where `Sequence` or `Mapping` would accept more callers.
- Blanket `# type: ignore` without an error code, which hides later, unrelated errors on the same line.
- `isinstance` against a `runtime_checkable` Protocol as validation of method signatures.
- Overloads whose implementation signature does not cover every overload.

## Suggested Extension

Type a small LLM client library end to end: `TypedDict` messages with `Literal` roles, a `Protocol` for providers, an `@overload` for `complete(..., stream: Literal[True]) -> AsyncIterator[str]` versus `stream: Literal[False] -> str`, and a `ParamSpec` retry decorator. Run `mypy --strict` and `pyright` on it and reconcile any differences between the two tools.
