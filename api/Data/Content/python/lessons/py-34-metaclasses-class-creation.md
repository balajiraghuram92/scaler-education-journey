# Metaclasses and Class Creation

Metaclasses are the machinery behind Django models, `enum.Enum`, `abc.ABC` and Pydantic's `BaseModel`, so you meet their effects daily even if you rarely write one. Interviewers use them to test whether you know what a `class` statement actually does and, more importantly, whether you have the judgement to say "you don't need a metaclass here". A senior answer explains the mechanism, then names the lighter tools (`__init_subclass__`, `__set_name__`, class decorators) that solve 95% of the same problems.

## Concepts Covered

### Classes are objects created by `type`

In Python a class is an ordinary object, and `type` is the default class of classes (its **metaclass**). Calling `type(name, bases, namespace)` builds a class dynamically; the `class` statement is syntax for the same thing.

```python
def greet(self):
    return f"hi {self.name}"

User = type("User", (), {"greet": greet, "__init__": lambda self, n: setattr(self, "name", n)})
print(User("ana").greet(), type(User), type(type), User.__mro__)
```

```text
hi ana <class 'type'> <class 'type'> (<class '__main__.User'>, <class 'object'>)
```

`type(type)` is `type`, which is why the chain "instance, class, metaclass" ends there. Dynamic creation is how libraries generate classes from a schema, a database table or an OpenAPI document at runtime.

### What the `class` statement does, step by step

For `class Thing(Base, metaclass=Meta, flavor="x"): ...` the interpreter does the following:

1. Resolve bases (a base object may supply `__mro_entries__`, which is how `typing.Generic[T]` becomes a real base class).
2. Pick the metaclass: the explicit `metaclass=` keyword, otherwise the most derived metaclass among the bases, otherwise `type`.
3. Call `Meta.__prepare__(name, bases, **kwargs)` to get the **namespace** mapping the body will execute in.
4. Execute the class body in that namespace.
5. Call `Meta(name, bases, namespace, **kwargs)`, which runs `Meta.__new__` then `Meta.__init__`.

Inside `type.__new__` two more hooks fire: each attribute's `__set_name__(owner, name)` is called, then the parent's `__init_subclass__`. You can see the order directly:

```python
class Meta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kw):
        print("prepare", name, kw)
        return {}

    def __new__(mcs, name, bases, ns, **kw):
        print("new", name, sorted(k for k in ns if not k.startswith("__")))
        return super().__new__(mcs, name, bases, ns)

    def __init__(cls, name, bases, ns, **kw):
        print("init", name)
        super().__init__(name, bases, ns)

class Desc:
    def __set_name__(self, owner, name):
        print("set_name", name, owner.__name__)

class Base:
    def __init_subclass__(cls, **kw):
        print("init_subclass", cls.__name__, kw)
        super().__init_subclass__()

class Thing(Base, metaclass=Meta, flavor="x"):
    a = Desc()
```

```text
prepare Thing {'flavor': 'x'}
new Thing ['a']
set_name a Thing
init_subclass Thing {}
init Thing
```

Notice two things. `__set_name__` and `__init_subclass__` run **inside** `Meta.__new__` (when it calls `type.__new__`), before `Meta.__init__`. And the `flavor` keyword reached `__prepare__` and `__new__` but not `__init_subclass__`, because `Meta.__new__` did not forward `**kw` to `super().__new__`. Forgetting to forward class keywords is a common bug when you wrap `type.__new__`.

### `__init_subclass__`: the first tool to reach for

`__init_subclass__` (3.6+) is a hook on a **base class** that runs every time it is subclassed. It covers plugin registration, validation of subclass contracts, and automatic configuration, with no metaclass at all and with no metaclass conflicts.

```python
class Provider:
    registry: dict[str, type["Provider"]] = {}

    def __init_subclass__(cls, *, name: str | None = None, **kw):
        super().__init_subclass__(**kw)
        key = name or cls.__name__.lower()
        if key in Provider.registry:
            raise TypeError(f"duplicate provider {key!r}")
        Provider.registry[key] = cls

class OpenAI(Provider): ...
class Local(Provider, name="llama"): ...

print(sorted(Provider.registry))
try:
    class Dup(Provider, name="llama"): ...
except TypeError as e:
    print(e)
```

```text
['llama', 'openai']
duplicate provider 'llama'
```

This is how an LLM gateway discovers its provider adapters without a hand-maintained `if/elif` chain. Always call `super().__init_subclass__(**kw)` so cooperative multiple inheritance keeps working.

### Class decorators versus metaclasses

A class decorator receives the finished class and returns a class (usually the same one, modified). It cannot influence how the class body executes or what the namespace is, and it is **not inherited** by subclasses. A metaclass or `__init_subclass__` applies to every subclass automatically.

| Need | Best tool |
|---|---|
| Add or wrap attributes on one class (e.g. `@dataclass`) | Class decorator |
| Register or validate every subclass | `__init_subclass__` |
| Name-aware field objects | Descriptor with `__set_name__` |
| Control the class namespace or the class object's creation (custom `__prepare__`, ordering, rejecting duplicates) | Metaclass |
| Change how instances are created (`Cls()`) at the class level, such as a singleton | Metaclass `__call__` (or a module-level instance) |
| Make `isinstance` or `issubclass` behave specially | Metaclass `__instancecheck__` / `__subclasscheck__` (as `abc` does) |

### Metaclass conflicts

A class has exactly one metaclass, and it must be a subclass of the metaclasses of all its bases. Mixing two unrelated metaclasses raises `TypeError`. The classic trigger is combining an `ABC` (metaclass `ABCMeta`) with a framework class that has its own metaclass, such as an ORM model or an `Enum`.

```python
class M1(type): ...
class M2(type): ...
class A(metaclass=M1): ...
class B(metaclass=M2): ...

try:
    class C(A, B): ...
except TypeError as e:
    print(e)

class M3(M1, M2): ...        # a common derived metaclass resolves it
class C2(A, B, metaclass=M3): ...
print(type(C2).__name__)
```

```text
metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
M3
```

The fix is to create a metaclass that inherits from both. Pydantic's `ModelMetaclass` and Django's model metaclass are examples of libraries that deliberately subclass `ABCMeta` or cooperate so users can mix in abstract bases. Needing this fix at all is a hint that you chose a metaclass where `__init_subclass__` would have avoided the conflict.

### A realistic metaclass: collecting declared fields

Django-style models and legacy SQLAlchemy `declarative_base()` collect `Field` attributes into a schema when the class is created. Here is the idea in a few lines, followed by the same behaviour using only `__init_subclass__`:

```python
class Field:
    def __init__(self, column_type):
        self.column_type = column_type

    def __set_name__(self, owner, name):
        self.name = name

class ModelMeta(type):
    def __new__(mcs, name, bases, ns):
        cls = super().__new__(mcs, name, bases, ns)
        fields = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "_fields", {}))
        fields.update({k: v for k, v in ns.items() if isinstance(v, Field)})
        cls._fields = fields
        cls._table = ns.get("__tablename__", name.lower() + "s")
        return cls

class Model(metaclass=ModelMeta):
    @classmethod
    def create_sql(cls):
        cols = ", ".join(f"{n} {f.column_type}" for n, f in cls._fields.items())
        return f"CREATE TABLE {cls._table} ({cols})"

class Ticket(Model):
    id = Field("INTEGER PRIMARY KEY")
    title = Field("TEXT")

class Bug(Ticket):
    severity = Field("INTEGER")

print(Ticket.create_sql())
print(Bug.create_sql())
```

```text
CREATE TABLE tickets (id INTEGER PRIMARY KEY, title TEXT)
CREATE TABLE bugs (id INTEGER PRIMARY KEY, title TEXT, severity INTEGER)
```

The same collection works with a plain base class:

```python
class Model2:
    _fields: dict = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        fields = dict(getattr(cls.__mro__[1], "_fields", {}))
        fields.update({k: v for k, v in vars(cls).items() if isinstance(v, Field)})
        cls._fields = fields
```

Modern SQLAlchemy 2.0's `DeclarativeBase` uses `__init_subclass__` rather than a metaclass for exactly this reason, whereas Pydantic v2 and Django still use metaclasses because they need to intercept class creation earlier (for example to build a validator from annotations before the class is usable).

### `__prepare__`, `__call__` and typing

Since dicts preserve insertion order (3.7+), `__prepare__` is rarely needed to keep field order. Its real uses are returning a custom mapping: for instance, one that rejects duplicate method definitions, or that records how names are looked up. A metaclass `__call__` runs when you write `Cls(...)` and can implement singletons or pooling, but a module-level instance is simpler and testable.

> **Pitfall:** Attributes created by a metaclass are invisible to static type checkers. Libraries that generate `__init__` signatures or fields (Pydantic, attrs, dataclasses) rely on `typing.dataclass_transform` (PEP 681) to tell tools what they do. A homemade metaclass that adds `__init__` will fail type checks unless you provide stubs or the same decorator.

## Practical Backend Scenario

An LLM gateway supports OpenAI, Anthropic and a self-hosted model. Each provider adapter must expose `name`, `complete()` and `stream()`, and the gateway must find adapters by name from configuration. The first version used a metaclass to register adapters and an `ABC` for the interface, and the team immediately hit "metaclass conflict" when one adapter also inherited from an ORM-backed mixin. The fix was to delete the metaclass: `Provider.__init_subclass__(cls, *, name)` registers the class and checks that required methods are overridden, while the interface is a `Protocol` for typing. Registration, validation and error messages stayed at class-creation time (so a typo fails at import, not mid-request), and the conflict disappeared.

## Practice Loop

1. Create a class with `type("Name", bases, ns)` and prove it equals one built with the `class` statement by comparing `__mro__`, `__dict__` keys and `type(cls)`.
2. Reproduce the hook-order demo, then change `Meta.__new__` to forward `**kw` to `type.__new__` and observe `flavor` arrive in `__init_subclass__`.
3. Implement the provider registry with `__init_subclass__`, add duplicate-name detection, and write a pytest test that a duplicate raises `TypeError` at class definition.
4. Trigger a metaclass conflict by combining `ABC` with a custom metaclass, then resolve it with a derived metaclass.
5. Re-implement the `Model`/`Field` collector as a metaclass, then as `__init_subclass__`, and compare the line count and inheritance behaviour.
6. Write a `__prepare__` that returns a dict subclass rejecting duplicate method names, and show the resulting error.

## Evidence of Understanding

- I can describe the sequence `__prepare__`, body execution, `__new__`, `__set_name__`, `__init_subclass__`, `__init__` and state which hooks run inside `type.__new__`.
- I can explain why `type(type) is type` and build a class with the three-argument `type` call.
- I can choose among a class decorator, `__init_subclass__`, a descriptor and a metaclass for a given requirement, and justify the choice.
- I can explain a metaclass conflict and resolve it, and say how to avoid it in the first place.
- I can read the source of an ORM or Pydantic-style model and say what its metaclass is doing at class-creation time.
- I can name the type-checking cost of metaclass-generated attributes.

## Interview Questions to Rehearse

### Q: What is a metaclass, and what happens when Python executes a `class` statement?

A metaclass is the class of a class; `type` is the default. The statement resolves bases, selects the metaclass, calls `__prepare__` for the namespace, runs the body in it, and then calls the metaclass with `(name, bases, namespace)`, which runs `__new__` and `__init__`. `type.__new__` also calls each attribute's `__set_name__` and the parent's `__init_subclass__`.

### Q: When would you actually write a metaclass?

When you must control how the class object is built or how the class behaves as an object: a custom `__prepare__` namespace, `__instancecheck__` or `__subclasscheck__` customization, intercepting class-level attribute access, or generating classes before they are usable (Django models, Pydantic). If the need is "do something for each subclass" use `__init_subclass__`; if it is "add behaviour to this class" use a decorator.

### Q: What is the difference between `__init_subclass__` and a class decorator?

`__init_subclass__` lives on a base class and runs automatically for every descendant, so it enforces policy across a hierarchy. A class decorator runs once, on the class it decorates, and is not inherited. The decorator receives the finished class and can only post-process it; `__init_subclass__` also runs after creation, but it applies by inheritance and can take class keyword arguments.

### Q: Explain a "metaclass conflict" and how you fix it.

A class's metaclass must be a subclass of every base's metaclass. If two bases have unrelated metaclasses, Python cannot choose, so it raises `TypeError`. Fix it by defining a metaclass that inherits from both and passing it explicitly, or, better, remove the need for one of the metaclasses by switching to `__init_subclass__`.

### Q: How do Django, SQLAlchemy and Pydantic use class creation?

Django's `ModelBase` metaclass gathers fields and builds `_meta`. Pydantic v2's `ModelMetaclass` inspects annotations and builds a validator and serializer when the model class is created. SQLAlchemy 2.0's `DeclarativeBase` uses `__init_subclass__` to map classes, while the legacy `declarative_base()` function relied on a metaclass. The common thread is turning declarative class bodies into schema at class-creation time.

### Q: What goes wrong when a metaclass adds `__init__` or fields, from a tooling perspective?

Static analyzers see only what is written in the source, so generated signatures and attributes are invisible, producing false positives for users. Libraries solve it with `dataclass_transform` (PEP 681) or by shipping type stubs. Another cost is debuggability: stack traces and `help()` show synthetic code.

## Common Pitfalls

- Reaching for a metaclass when `__init_subclass__`, a decorator or a descriptor would do.
- Not forwarding `**kwargs` to `super().__new__` / `super().__init_subclass__`, which swallows class keyword arguments or breaks cooperative inheritance.
- Combining metaclass-bearing bases (ABC plus ORM plus Enum) without a combined metaclass.
- Mutating the namespace in `__new__` after calling `super().__new__`, which no longer affects the class; set attributes on `cls`.
- Singleton metaclasses that make tests share state and are unsafe under threads without a lock.
- Registering classes at import time and forgetting that only imported modules register, so plugins in unimported files are missing.
- Expecting `__init_subclass__` to run for the base class itself; it only runs for subclasses.

## Suggested Extension

Build a tiny validation framework in two ways: first with a metaclass that reads annotations in `__new__` and generates `__init__`, then with `__init_subclass__` and `__set_name__`. Add `typing.dataclass_transform` to the base to see a type checker pick up the generated signature, and write a short note comparing the failure modes: import-time errors, subclassing, and tooling support.
