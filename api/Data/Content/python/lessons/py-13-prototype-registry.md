# Design Patterns: Prototype and Registry

Prototype and Registry answer two questions that every plugin-style backend meets: "how do I make many similar objects without redoing expensive setup?" and "how do I find the right implementation or template by name?" In Python the first is mostly solved by the `copy` module and the second by a dictionary, so the interview is really about the details: shallow versus deep copies, what to share and what to clone, concurrency around the registry, and how plugins get registered in the first place.

## Concepts Covered

### The Prototype idea and what Python already gives you

The Prototype pattern creates a new object by copying an existing, fully configured one instead of building it from scratch. The motivation is the same as cloning a golden VM image: the base object already carries the slow or tedious configuration (a loaded prompt template, a populated invoice, a test user), and each copy only needs a few instance-specific changes such as a hostname or a query. The hand-written version gives the class a `clone()` method, so the object owns its copying logic and callers never reach into its fields. That solves three problems of copying from outside: coupling to private fields, forgetting a field when one is added, and `isinstance` chains for subclasses.

A caution from the lecture applies when you write `clone()` by hand: every subclass that adds fields must override it, otherwise the parent's `clone()` runs and silently returns a plain parent object without the subclass's data. Python offers a better default. `copy.copy` and `copy.deepcopy` reconstruct the object's real class, so a `Dog` copied through `copy.copy` is still a `Dog` with its `breed`. Prefer the standard library and write `clone()` only as a thin, named wrapper.

Python also cannot overload constructors, so the Java idiom of a second `__init__` that takes a source object does not work: the second definition replaces the first. Use `copy`, a `classmethod` such as `from_template`, or `dataclasses.replace`.

### Shallow versus deep copy

A shallow copy creates a new outer object but shares the nested objects. A deep copy recursively copies everything. The difference decides whether a clone is really independent:

```python
import copy


class Config:
    def __init__(self) -> None:
        self.settings = {"debug": True}


original = Config()
shallow = copy.copy(original)
shallow.settings["debug"] = False
print(original.settings["debug"])         # False: the dict is shared

deep = copy.deepcopy(original)
deep.settings["debug"] = True
print(original.settings["debug"], deep.settings["debug"])   # False True
```

The same trap appears when a hand-written copy constructor does `self.installed_packages = source.installed_packages`: both objects now point at one list. The fix is `list(source.installed_packages)` or a `deepcopy`. Immutable parts (strings, ints, tuples of immutables, frozen dataclasses, enum members) never need copying, and `deepcopy` returns the same object for them.

### Customising copies with `__deepcopy__` and the memo

Deep-copying everything is often wrong. An LLM prompt template should clone its few-shot examples, but it must share the HTTP client, the loaded tokenizer or the connection pool. Those objects are expensive, may hold locks or sockets, and `copy.deepcopy` of a `threading.Lock` raises `TypeError: cannot pickle '_thread.lock' object`. Implement `__deepcopy__(self, memo)` to decide per attribute:

```python
import copy


class PromptTemplate:
    def __init__(self, system: str, examples: list[str], client: object) -> None:
        self.system = system
        self.examples = examples
        self.client = client            # expensive and shared on purpose

    def __deepcopy__(self, memo: dict) -> "PromptTemplate":
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone          # register BEFORE recursing: handles cycles
        clone.system = self.system
        clone.examples = copy.deepcopy(self.examples, memo)
        clone.client = self.client
        return clone


base = PromptTemplate("Be terse.", ["Q: hi"], client=HttpClient())
c = copy.deepcopy(base)
c.examples.append("Q: bye")
print(base.examples, c.examples, c.client is base.client)
```

```text
['Q: hi'] ['Q: hi', 'Q: bye'] True
```

The `memo` dictionary maps `id(original)` to its copy for one `deepcopy` call. It does two jobs: it prevents infinite recursion on cyclic structures (two nodes pointing at each other copy correctly), and it preserves sharing inside the graph (a list referenced twice is copied once, so both references still point at the same new list). Always pass `memo` into nested `deepcopy` calls, and register the new object in it before copying children. `__copy__` is the analogous hook for shallow copies.

### The Registry: store templates, return clones

A registry is a keyed store of ready-made prototypes (or classes) that code can look up by name. The two patterns separate cleanly: Prototype copies an object, Registry stores and retrieves by key. The dangerous mistake is handing out the stored object itself. If `get("backend-server-v3")` returns the template and the caller sets `hostname` on it, the shared template is now modified for everyone. Return a clone, and fail loudly on a missing key, because `dict.get` returns `None` and the error only appears later when `.clone()` is called on `None`.

```python
import copy
import threading
from typing import Any


class TemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, Any] = {}
        self._lock = threading.Lock()

    def register(self, name: str, template: Any) -> None:
        with self._lock:                       # check-then-act must be atomic
            if name in self._templates:
                raise KeyError(f"already registered: {name}")
            self._templates[name] = template

    def get(self, name: str) -> Any:
        try:
            return copy.deepcopy(self._templates[name])
        except KeyError:
            raise KeyError(f"unknown template {name!r}; known: {sorted(self._templates)}") from None
```

An `if key not in d: d[key] = v` sequence is two steps, so two threads can both pass the check before either writes. Individual dict operations are atomic in CPython, but compound ones are not, and free-threaded 3.13t makes disciplined locking more important, not less. Reads after start-up are usually lock-free in practice because registration happens at import or boot.

### Three ways to register implementations

A registry of classes (rather than prototype instances) is how providers, embedders and notification channels are found by name. Python gives three registration styles, each trading explicitness for convenience:

```python
class Provider:
    registry: dict[str, type["Provider"]] = {}

    def __init_subclass__(cls, /, name: str | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__.lower()
        if key in Provider.registry:
            raise TypeError(f"duplicate provider {key!r}")
        Provider.registry[key] = cls


class OpenAIProvider(Provider, name="openai"): ...
class LocalProvider(Provider): ...                  # registered as "localprovider"


EMBEDDERS: dict[str, type] = {}

def register_embedder(name: str):
    def decorator(cls):
        EMBEDDERS[name] = cls
        return cls
    return decorator

@register_embedder("hash")
class HashEmbedder: ...
```

`__init_subclass__` registers every subclass at class-creation time with no decorator, and it can reject duplicates. The decorator is explicit and works on classes you do not want to make subclasses. Both share a hidden requirement: the module defining the class must actually be imported before lookup, so a registry silently looks empty if nobody imports the plugin. For third-party packages the standard solution is entry points: a package declares a name in its `pyproject.toml` under a group, and the host discovers it without importing anything up front.

```python
from importlib.metadata import entry_points

def load_embedders() -> dict[str, type]:
    return {ep.name: ep.load() for ep in entry_points(group="myapp.embedders")}
```

```toml
[project.entry-points."myapp.embedders"]
openai = "myapp_openai.embedder:OpenAIEmbedder"
```

`entry_points(group=...)` is the modern selectable API (Python 3.10+). Loading is deferred until `ep.load()`, which keeps start-up fast and lets you skip plugins whose optional dependencies are missing.

### When to skip Prototype

If constructing a fresh object is cheap, cloning only adds code and a way to share state by accident. Prototype earns its place when construction is slow (fetching from a database, loading configuration), when objects need many identical settings plus a few changes (test fixtures, request templates), or when you must create copies of a runtime-chosen subclass without knowing its type. A frozen dataclass with `dataclasses.replace` is often the lighter alternative.

## Practical Backend Scenario

A platform team ships a document-processing service with three tenants, each having a prompt template, few-shot examples and a shared model client. Building a template per request re-reads files and re-initialises clients, adding 80 ms of latency. They register one prototype per tenant at start-up and serve `registry.get(tenant)`, a clone whose `__deepcopy__` copies the examples and shares the client. A production bug appears when a developer mutates the template returned by an earlier version of `get()` that did not clone: tenant A's per-request footer leaks into tenant B's prompts. The fix is the clone-on-get rule plus a test that mutates a result and re-fetches. New model providers are added as separate packages through entry points, so the core service never changes.

## Practice Loop

1. Reproduce the shared-settings bug with `copy.copy`, then fix it with `copy.deepcopy`.
2. Write `PromptTemplate.__deepcopy__` that shares the client but copies the examples, and assert both properties.
3. Build `TemplateRegistry`, then write a test that mutates a fetched clone and checks the next `get` is unchanged.
4. Hammer `register` from 8 threads with the same key and show exactly one succeeds; remove the lock and observe what happens.
5. Implement all three registration styles for a `Notifier` family and add a duplicate-name check to each.

## Evidence of Understanding

- You can explain why `copy.copy` shares nested mutables and `copy.deepcopy` does not.
- You can write `__deepcopy__` with `memo` and explain what the memo prevents.
- You can say what should be shared and what should be cloned in an object that holds a client.
- You can state why a registry must return clones and why `get` should raise on a missing key.
- You can explain the race in check-then-add and the fix.
- You can compare `__init_subclass__`, decorators and entry points, including the import-time caveat.

## Interview Questions to Rehearse

### Q: What is the difference between `copy.copy` and `copy.deepcopy`?
`copy.copy` creates a new top-level object but its attributes still reference the same nested objects, so mutating a nested list or dict affects both. `copy.deepcopy` recursively copies the whole graph, using a memo to handle cycles and shared references. I choose shallow when nested parts are immutable or intentionally shared, and deep when the clone must be fully independent.

### Q: How do you stop `deepcopy` from copying a database connection?
Define `__deepcopy__(self, memo)` and assign the connection by reference while deep-copying the data fields, passing `memo` along. I can also keep the connection outside the object and inject it. Deep-copying locks, sockets and file handles either fails or produces something broken.

### Q: Why must a prototype registry return a clone?
Because the registry owns the template and many callers use it. If it returns the stored object, any caller's modification changes the template for everyone, which becomes a cross-request data leak. Returning a clone, and testing that mutating the result does not change the next fetch, keeps templates pristine.

### Q: How would you let third parties add providers without changing your code?
Use entry points. Packages declare themselves under a group in `pyproject.toml`, and the host calls `importlib.metadata.entry_points(group=...)` and loads the ones it needs lazily. For in-repo plugins I would use `__init_subclass__` or a decorator, with duplicate detection, and make sure the plugin modules are imported.

### Q: Is a registry thread-safe in CPython because of the GIL?
Single dict operations are atomic, but check-then-act sequences are not. Two threads can both see a key missing and both insert. I guard registration with a lock, or populate the registry at start-up before serving requests and treat it as read-only afterwards.

## Common Pitfalls

- Using `copy.copy` on an object that contains lists or dicts and assuming the clone is independent.
- Returning the stored prototype from `get()` instead of a clone.
- Calling `registry.get(key)` with a typo and getting `None`, then failing later with an `AttributeError`.
- Deep-copying objects that hold locks, clients or file handles instead of sharing them deliberately.
- Forgetting to register `self` in `memo` before copying children, causing recursion on cyclic data.
- Writing a manual `clone()` and forgetting to override it in a subclass.
- Relying on `__init_subclass__` or decorators without importing the plugin modules.

## Suggested Extension

Build a `NotifierRegistry` that loads built-in notifiers through `__init_subclass__` and third-party ones through entry points, rejects duplicate names, and returns a configured clone per request. Add a test package that declares an entry point in a temporary `pyproject.toml` or `dist-info` directory and verify the host discovers it without importing it explicitly.
