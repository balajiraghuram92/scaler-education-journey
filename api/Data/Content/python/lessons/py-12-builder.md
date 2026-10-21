# Design Patterns: Builder

Builder is the pattern you meet whenever an object has many optional settings that must be valid together: an LLM request, a database configuration, a query, a notification. Interviewers ask about it to see whether you can separate "collecting values" from "creating a valid object", and, in Python, whether you know when plain keyword arguments and a frozen dataclass already solve the problem. A senior answer names both the pattern and the point at which it stops paying for itself.

## Concepts Covered

### The problem: constructors that do not scale

A `Student` with name, age, grade, batch, ID, university, graduation year and phone has eight constructor parameters. Callers must pass them in order, cannot tell which `None` means "unknown", and validation rules that span fields ("graduation year must not be later than 2022") have no obvious home. Java solves this with overloaded constructors, which become error-prone as fields are added. Python cannot overload constructors at all: a second `__init__` silently replaces the first. Python's built-in answer is keyword arguments with defaults, and it takes you surprisingly far.

### Start with kwargs and a frozen dataclass

Before writing a builder, try this. Keyword-only fields make the call site self-documenting, defaults cover the optional values, `frozen=True` gives immutability, and `__post_init__` validates cross-field rules before the object can exist.

```python
from dataclasses import dataclass, field, replace


@dataclass(frozen=True, kw_only=True, slots=True)
class DbConfig:
    url: str
    username: str
    password: str = field(repr=False)
    max_connections: int = 10
    read_only: bool = False
    allowed_hosts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.url.startswith(("postgresql://", "mysql://")):
            raise ValueError(f"unsupported url: {self.url!r}")
        if not 1 <= self.max_connections <= 500:
            raise ValueError("max_connections must be 1..500")


cfg = DbConfig(url="postgresql://db/app", username="svc", password="s3cret", max_connections=20)
print(cfg)
print(replace(cfg, read_only=True).read_only)
```

```text
DbConfig(url='postgresql://db/app', username='svc', max_connections=20, read_only=False, allowed_hosts=())
True
```

Assigning `cfg.max_connections = 5` raises `FrozenInstanceError`, and `replace` gives you the "copy with one change" operation for free. For a class with a few fields and no multi-step assembly, this is the honest answer to "should I use a Builder?" and it is exactly the point of the lecture's wrap-up: a `Point(x, y)` does not need one.

### When a real Builder earns its place

Reach for a builder when values arrive gradually over several steps (a prompt assembled from system text, retrieved passages and the user turn), when many optional parts need readable chaining, when validation depends on several fields together, or when you want one construction process to produce differently shaped products. The structure is a mutable builder that collects values, setters that return `self` so calls chain, and a `build()` that validates and then creates the product.

```python
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class ChatRequest:
    model: str
    messages: tuple[tuple[str, str], ...]
    temperature: float
    max_tokens: int

    @staticmethod
    def builder() -> "ChatRequestBuilder":
        return ChatRequestBuilder()


class ChatRequestBuilder:
    def __init__(self) -> None:
        self._model: str | None = None
        self._messages: list[tuple[str, str]] = []
        self._temperature = 0.2
        self._max_tokens = 512

    def model(self, name: str) -> Self:
        self._model = name
        return self

    def system(self, text: str) -> Self:
        self._messages.append(("system", text))
        return self

    def user(self, text: str) -> Self:
        self._messages.append(("user", text))
        return self

    def max_tokens(self, value: int) -> Self:
        self._max_tokens = value
        return self

    def build(self) -> ChatRequest:
        if self._model is None:
            raise ValueError("model is required")
        if not any(role == "user" for role, _ in self._messages):
            raise ValueError("at least one user message is required")
        roles = [role for role, _ in self._messages]
        if "system" in roles and roles.index("system") != 0:
            raise ValueError("system message must come first")
        return ChatRequest(self._model, tuple(self._messages), self._temperature, self._max_tokens)
```

Three details matter. First, every setter returns `self`; forget one and `Builder().set_name("x").build()` fails with `AttributeError: 'NoneType' object has no attribute 'build'`. Second, `-> Self` (Python 3.11+) keeps chaining correctly typed when someone subclasses the builder. Third, `ChatRequest.builder()` is a static entry point so callers discover the builder from the product class without importing a second name.

### Where validation lives

Per-field checks can live in setters, but rules that involve several fields (a user message must exist, the system message must come first) can only be checked once everything is set, so they belong in `build()` or in the product's `__post_init__`. The goal is that an invalid object can never exist: a `Message` of type text with empty content must fail at build time, not three calls later in a worker. Checking in `build()` also gives you one place to raise a precise error instead of scattering partial checks.

### Immutability and the sharing traps

Three bugs recur in review. The first is a `build()` that returns the builder's own mutable instance: after `c1 = b.v(1).build(); c2 = b.v(2).build()`, `c1.v` is `2` and `c1 is c2` is `True`, because both names point at the object the builder keeps mutating. `build()` must construct a fresh product. The second is sharing a list: if the product stores `tags` by reference, changing the original list afterwards changes the built object too.

```python
tags = ["a"]
bad = Bad(tags)             # self.tags = tags
tags.append("b")
print(bad.tags)             # ['a', 'b']  shared state

good = Good(tags[:1])       # self.tags = tuple(tags)
print(good.tags)            # ('a',)
```

Copy collections at the boundary (`tuple(...)` or `list(...)`) in `build()`. The third is the mutable default argument: `def add_item(cart=[])` evaluates the default once at definition time, so two calls print `['apple']` then `['apple', 'apple']`. Use `None` plus a fresh list inside, or a `field(default_factory=list)`. Finally, `__slots__` on a helper class turns a typo like `h.nmae = "Riya"` into an immediate `AttributeError` instead of a silent new attribute, which is a cheap guard for hand-written builders.

### Functional and generative builders

An alternative avoids the reuse problem entirely: each setter returns a new immutable builder instead of mutating. SQLAlchemy's `select(...).where(...).order_by(...)` works this way, which is why you can safely keep a base query and derive variants from it. In Python you can get the same effect with a frozen dataclass and `dataclasses.replace`:

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class QueryBuilder:
    table: str = ""
    columns: tuple[str, ...] = ("*",)
    conditions: tuple[str, ...] = ()

    def select(self, *columns: str) -> "QueryBuilder":
        return replace(self, columns=columns)

    def from_(self, table: str) -> "QueryBuilder":
        return replace(self, table=table)

    def where(self, condition: str) -> "QueryBuilder":
        return replace(self, conditions=self.conditions + (condition,))   # accumulate, never overwrite

    def build(self) -> str:
        if not self.table:
            raise ValueError("from_() is required")
        sql = f"SELECT {', '.join(self.columns)} FROM {self.table}"
        return sql + (" WHERE " + " AND ".join(self.conditions) if self.conditions else "")


base = QueryBuilder().select("name", "age").from_("users")
print(base.where("age > 18").where("active = true").build())
print(base.build())
```

```text
SELECT name, age FROM users WHERE age > 18 AND active = true
SELECT name, age FROM users
```

The base builder is untouched by the derived one. The cost is an object allocation per step, which is irrelevant for configuration and request assembly but not for tight loops. (Real SQL should use bound parameters, never string-built conditions; this sketch only shows the pattern.)

### Honest trade-offs

A builder doubles the surface area: every new field needs a field, a setter and a build line. If the product has five fields and no cross-field rules, kw-only arguments win. If it needs staged assembly, readable chaining or several valid constructions, a builder wins. For configuration read from the environment, a Pydantic model or settings class does the same job with validation built in, so mention that you would not hand-roll a builder there.

## Practical Backend Scenario

An FDE integrating a customer's support bot assembles requests in four places: a retrieval step adds passages, a policy step adds a system prompt, a guardrail step sets token limits, and a cost step picks the model. Each place used a dict, and a typo in one produced a request with `temprature` silently ignored by the SDK, which went unnoticed for a week. Replacing the dict with a `ChatRequestBuilder` fixes it twice: setters catch the typo immediately (`AttributeError` on an unknown method), and `build()` enforces "a user message exists" and "max tokens fits the budget" for every caller. The built `ChatRequest` is frozen, so a retry layer can resend the same request object without worrying that a middleware mutated it.

## Practice Loop

1. Build `DbConfig` with keyword arguments and `__post_init__` validation. Try to mutate it and observe `FrozenInstanceError`.
2. Write the `ChatRequestBuilder`, then add a test that proves two `build()` calls return different objects and that mutating the builder afterwards does not change the first request.
3. Add `allowed_hosts` to the product. First store the list by reference and reproduce the sharing bug, then fix it with `tuple(...)` in `build()`.
4. Reproduce the `cart=[]` default bug and the `__slots__` typo error.
5. Rewrite the builder as a functional builder using `dataclasses.replace` and compare the code you had to write.

## Evidence of Understanding

- You can explain why Python has no overloaded constructors and what replaces them.
- You can argue when keyword-only arguments and a frozen dataclass are enough.
- You can explain why `build()` must return a new object and why cross-field validation belongs there.
- You can show and fix the shared-list and mutable-default bugs.
- You can explain what `return self` buys and what `Self` adds for subclasses.
- You can describe a generative builder and name a library that uses one.

## Interview Questions to Rehearse

### Q: Why use a Builder instead of one large constructor?
A large constructor forces callers to supply everything at once in the right order and gives validation no natural place. A builder lets values arrive step by step, reads clearly through named setters, and centralises validation in `build()` so an invalid object cannot be created. In Python I would first ask whether keyword-only arguments plus a frozen dataclass already give me that.

### Q: Where should multi-field validation live, and why?
In `build()` or the product's `__post_init__`, because only then are all fields known. Per-setter validation cannot see fields that have not been set yet. Putting it in the constructor path also guarantees that nothing, including code that bypasses the builder, can create an invalid instance.

### Q: What are the classic bugs in a hand-written builder?
A `build()` that returns the builder's own instance, so later changes alter earlier products; storing collections by reference; a setter that overwrites instead of appending (a query builder that keeps only the last `where`); a forgotten `return self`; and mutable default arguments. Each is a one-line fix, but each is easy to miss without a test that builds twice.

### Q: How would you make a builder safe to reuse as a template?
Make the product immutable and either copy in `build()` or make the builder itself immutable so each setter returns a new builder. SQLAlchemy's generative `select()` is the standard example: deriving a variant never changes the base query.

### Q: When is Builder overkill in Python?
When there are few fields, no cross-field rules and no staged assembly. `Point(x, y)` or a small `@dataclass(kw_only=True)` is clearer, and `dataclasses.replace` covers copy-with-change. I would also use a Pydantic model for environment-driven configuration rather than hand-writing builders.

## Common Pitfalls

- `build()` returning the builder's internal mutable object.
- Storing list or dict arguments without copying them.
- Setters that overwrite when the field is meant to accumulate (several `where` clauses).
- Forgetting `return self` on one setter, which breaks chains with a confusing `NoneType` error.
- Mutable default arguments such as `cart=[]` in builders and constructors.
- Putting cross-field validation in setters, where it runs before all values exist.
- Using a builder for a two-field class because the pattern feels senior.

## Suggested Extension

Add `from_request(existing)` to `ChatRequestBuilder` so retries can start from a built request and change one field, then add a `PromptBuilder` director that assembles system text, retrieved passages and the user question in a fixed order. Write a property-style test that builds 100 random valid requests and checks that none of them can be mutated.
