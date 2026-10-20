# Design Patterns: Introduction and Singleton

Design patterns are named, reusable answers to recurring structural problems, and interviewers use them as shorthand to test whether you can reason about trade-offs rather than recite UML. The Singleton is the pattern most often asked about and most often misused: in Python it is both trivially easy to get (every module already is one) and surprisingly easy to get wrong (races, re-running `__init__`, pickling, tests that leak state, and one "singleton" per worker process). This lesson gives you the idiomatic options and, just as important, the grounds on which to refuse the pattern.

## Concepts Covered

### What patterns are for, and what they cost

A pattern is a vocabulary item: saying "the gateway is a factory behind a Protocol" compresses a paragraph of design into one sentence. Patterns fall into creational (how objects are made: Singleton, Builder, Prototype, Factory), structural (how they are composed: Adapter, Facade, Decorator) and behavioural (how they interact: Strategy, Observer). Python's first-class functions, modules and duck typing make several of them nearly free, so the senior question is never "which pattern fits?" but "does this problem actually exist here, and is the pattern's cost lower than the problem's?"

### The Singleton contract and its legitimate uses

The Singleton guarantees one instance per process and a global access point. The guarantee is justified when a resource is expensive to create or must be coordinated: a database engine and its connection pool, an HTTP client with a shared connection pool and rate-limit state, a loaded embedding model, a logging registry, a settings object. Python itself ships examples: `logging.getLogger(name)` returns the same logger for the same name, and `Enum` members are unique, so `Mode.SINGLE is Mode.SINGLE` is always `True`. A class whose only trait is "I have lots of methods" is not a candidate.

### Module-level instance: the default answer

The import system caches a module in `sys.modules` after its first import, so every importer gets the same module object and therefore the same attributes. If `config.py` defines `value = 10`, then `import config` and `import config as config2` give two names for one module, and after `config.increase()` runs, `config2.value` is `15`. For most services, an instance created at module scope (`settings = Settings()`, `llm = build_client()`) is the whole pattern with no ceremony. Its cost is eager construction at import time: a slow constructor makes startup and every test import slow, and any failure surfaces at import.

### Lazy options and what goes wrong

Laziness delays construction until first use. The textbook version overrides `__new__`, and it hides a trap the first time you add `__init__`:

```python
class DBConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, url):
        self.url = url

db1 = DBConnection("db.prod")
db2 = DBConnection("db.staging")
print(db1 is db2, db1.url)
```

```text
True db.staging
```

`__new__` returns the cached object, but Python then calls `__init__` on whatever `__new__` returned, every time. The second call silently re-points the "single" production connection at staging. Guard initialisation or, better, avoid constructor arguments on a singleton. A class-decorator variant (`def singleton(cls): ...` returning a function) avoids the re-init but replaces the class with a function, so `isinstance(x, DBConnection)` and subclassing break, and `a is b` is `True` while `a.url` stays `db.prod`.

The bigger issue is concurrency. The GIL does not make "check, then create, then assign" atomic, because a thread switch can happen between the `is None` test and the assignment. With a slow constructor the race is easy to see:

```python
import threading, time

class Slow:
    _instance = None
    created = 0

    def __new__(cls):
        if cls._instance is None:
            time.sleep(0.01)                 # expensive setup
            cls._instance = super().__new__(cls)
            cls.created += 1
        return cls._instance
```

Eight threads calling `Slow()` produce eight objects and `created == 8`. The fix is **double-checked locking**: an unlocked fast-path check, then the lock, then a second check, because another thread may have created the instance while you waited for the lock.

```python
class Registry:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:               # fast path, no lock after warm-up
            with cls._lock:
                if cls._instance is None:       # re-check: someone may have won
                    cls._instance = super().__new__(cls)
        return cls._instance
```

Dropping the outer check is still correct but takes the lock on every call, which is wasted contention. On free-threaded 3.13t the lock matters even more, since the GIL no longer serialises bytecode at all. Reading a plain attribute without the lock is safe here because the assignment happens last, after the object is fully built.

### Reusing the behaviour: metaclass and `functools.cache`

When many classes need the behaviour, put it in a metaclass so they all get it without copy-paste:

```python
class SingletonMeta(type):
    _instances: dict[type, object] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class EmbeddingClient(metaclass=SingletonMeta): ...
```

Because `__call__` intercepts construction itself, `__init__` runs once. For a function-shaped singleton, `@functools.cache` on a zero-argument factory is the most Pythonic lazy form: `get_client()` returns the same object every time. But the documentation is explicit that the cache keeps its own structure consistent while the wrapped function may run more than once if several threads miss at the same moment. With a barrier and a sleeping constructor, eight threads built eight clients. If construction has side effects (opening pools, loading weights), wrap the first call in a lock.

### Pickle, copy and subprocesses

A metaclass or decorator singleton can be duplicated by `pickle.loads`, which rebuilds the object without calling your `__call__`; the `__new__` variant returns the singleton on unpickle but overwrites its state. If a singleton can cross a pickle boundary (multiprocessing, caches), define `__reduce__` to return `(get_instance, ())`. Also remember scope: a singleton lives in one process. Four `uvicorn` workers mean four "singletons", and a pool created before `fork` is shared with children in a way most drivers cannot survive, so create engines and clients in the app's lifespan or after the fork.

### Why singletons hurt testability

A singleton is global mutable state. One test mutates it, and the next test inherits the mutation, which produces order-dependent failures that disappear when run alone. It also hides dependencies: a function that calls `get_settings()` internally has an invisible input you cannot supply from a test without patching.

```python
os.environ["LLM_MODEL"] = "test-model"
print(get_settings())      # Settings(llm_model='test-model', ...)
os.environ["LLM_MODEL"] = "other"
print(get_settings())      # still 'test-model': cached
get_settings.cache_clear() # needed between tests
```

The mitigation is to keep the singleton at the edges and inject values inward. Build one instance at the composition root, pass it to constructors, and in FastAPI expose it through `Depends(get_settings)` so tests can use `app.dependency_overrides`. You keep "one instance" without making everything depend on a global.

## Practical Backend Scenario

An LLM gateway builds an `httpx.AsyncClient` per request, paying a TLS handshake on every call and exhausting sockets at peak. The fix is one shared client with a bounded connection pool, created in the application lifespan and exposed by a dependency. In an interview, the strong answer also covers the failure modes: each worker process has its own client, tests must be able to substitute a fake without monkeypatching, and a hot-reload in development must not leak a second pool.

## Practice Loop

1. Run the `DBConnection` example above and confirm `db1.url` becomes `db.staging`; then fix it so `__init__` runs once.
2. Reproduce the eight-instance race with `Slow`, then fix it with double-checked locking and confirm `created == 1`.
3. Write a `SingletonMeta` and apply it to two unrelated classes; assert each has its own single instance.
4. Use a `threading.Barrier` to show `@functools.cache` can construct more than once, then add a lock and re-run.
5. Write two tests that fail in the wrong order because of shared singleton state, then fix them with injection or `cache_clear()`.

## Evidence of Understanding

- You can explain why module-level instances are the default Python singleton and what they cost at import time.
- You can predict that `__new__`-based singletons re-run `__init__` on every call.
- You can describe the check-then-act race, why the GIL does not prevent it, and why double-checked locking needs both checks.
- You can say when `functools.cache` is and is not a safe singleton.
- You can name two ways pickling or multiple worker processes break the "one instance" claim.
- You can argue for injection over global access in a testable service.

## Interview Questions to Rehearse

### Q: How would you implement a thread-safe singleton in Python?
Start with the module-level instance, since module import is already once-only and, for imports, guarded by the import lock. If it must be lazy, use double-checked locking: an unlocked check for the fast path, then acquire a lock and check again before creating. For many classes, use a metaclass `__call__` with the same logic. I would also say I avoid constructor arguments on singletons.

### Q: Why is the second `None` check inside the lock necessary?
Because another thread may have created the instance while this one was blocked waiting for the lock. Without the inner check, each waiting thread would create its own object in turn, and the guarantee of a single instance would be lost. The outer check exists only to avoid taking the lock after warm-up.

### Q: Does the GIL make a lazy singleton safe?
No. The GIL makes individual bytecodes atomic, not a compound check-then-assign sequence, and a thread switch can occur between the test and the assignment, especially when the constructor does I/O or sleeps. On free-threaded 3.13t there is no global serialisation at all. A lock is required.

### Q: What makes singletons hard to test, and what do you do about it?
They are global mutable state, so tests leak into each other, and callers have hidden dependencies that cannot be substituted. I create the instance once at the composition root and inject it, give module-level caches a `cache_clear()` hook for tests, and in FastAPI override the dependency instead of patching imports.

### Q: Is a singleton shared across your Gunicorn workers?
No. Each worker is a separate process with its own memory, so you get one instance per process. Anything that must be unique across processes, like a rate limiter or a lock, needs an external store such as Redis or the database. And resources like connection pools should be created after the fork.

## Common Pitfalls

- Calling the constructor with different arguments and getting the first instance back (or, with `__new__`, a silently re-initialised one).
- Checking `_instance is None` without a lock when construction is slow or has side effects.
- Using the decorator form and then breaking `isinstance`, subclassing, or type hints, because the name now refers to a function.
- Assuming `@functools.cache` runs the factory exactly once under concurrency.
- Letting module-level construction connect to a database at import time, which breaks tooling, tests and docs builds.
- Forgetting that pickling, `fork` and multiple workers each defeat "one instance per application".
- Using Singleton to avoid passing parameters, when the real fix is dependency injection.

## Suggested Extension

Implement a resettable `SingletonMeta` with a `clear()` class method for tests, add a `__reduce__` so unpickling returns the live instance, and write a pytest fixture that clears the registry after every test. Then rewrite one consumer to take the dependency as a constructor argument and compare how many lines of test setup you saved.
