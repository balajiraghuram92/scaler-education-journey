# Scopes, Closures and Descriptors

Closures and descriptors are the two mechanisms behind most of Python's "magic": decorators, bound methods, `property`, `classmethod`, ORM fields, Pydantic and dataclass fields, and `functools.cached_property` are all built from them. In production they explain bugs such as every tool in an agent registry calling the last tool, or a "read-only" attribute that is silently overwritten. In interviews, "walk me through what happens on `obj.attr`" is a standard senior-level probe.

## Concepts Covered

### Scope resolution: LEGB and the compile-time rule

Python resolves a name using Local, Enclosing function, Global (module) and Builtin scopes, in that order. The crucial detail is that the **compiler** decides, per function, which names are local: any name that is assigned, imported, or used as a loop variable anywhere in the function body is local for the entire body. Reading it before assignment therefore raises `UnboundLocalError`, not a fallback to the global.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        return x          # found in the enclosing scope
    return inner()

counter = 0

def bump():
    counter += 1          # assignment makes counter local to bump

print(outer())
try:
    bump()
except UnboundLocalError as e:
    print(type(e).__name__, e)
```

```text
enclosing
UnboundLocalError cannot access local variable 'counter' where it is not associated with a value
```

`global name` rebinds a module-level name; `nonlocal name` rebinds a name in the nearest enclosing function. Neither is needed to *mutate* an object (`registry.append(x)` is a load, not a rebind), only to *rebind* the name. Two scope rules surprise experienced engineers. First, **class bodies are not enclosing scopes**: a method cannot see a class variable by bare name, and neither can a comprehension nested inside the class body, except for its outermost iterable (this is unchanged by the 3.12 comprehension inlining in PEP 709). Second, `except E as e` deletes `e` at the end of the handler, so you cannot use it afterwards.

> **Pitfall:** `global` is often a sign of hidden shared state. Prefer passing state explicitly or encapsulating it in an object; the exception is deliberate module-level singletons such as a configured client.

### Closures and cell variables

A closure is a function plus the variables it captured from enclosing scopes. CPython stores each captured variable in a **cell** object shared between the outer and inner function; the inner function's `__closure__` holds the cells, and `__code__.co_freevars` names them. A closure captures the *variable* (the cell), not the value at definition time.

```python
def make_counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc

c = make_counter()
c()
print(c(), c.__code__.co_freevars, c.__closure__[0].cell_contents)
```

```text
2 ('n',) 2
```

This is the source of the classic **late-binding** bug. All closures created in a loop share the loop variable's cell, so they see its final value when finally called.

```python
from functools import partial

late = [lambda: i for i in range(3)]
print([f() for f in late])

bound_default = [lambda i=i: i for i in range(3)]
print([f() for f in bound_default])

bound_partial = [partial(lambda i: i, i) for i in range(3)]
print([f() for f in bound_partial])

def make(i):
    return lambda: i

print([make(i)() for i in range(3)])
```

```text
[2, 2, 2]
[0, 1, 2]
[0, 1, 2]
[0, 1, 2]
```

The fixes are to freeze the value (default argument, `functools.partial`) or to create a new scope per iteration with a factory function. The same bug appears with `def` inside a `for` loop that registers handlers by name, which is why it shows up in plugin, callback and tool-registration code.

> **Interview tip:** Say "closures capture variables, not values" and then show the default-argument fix and the factory fix. Mention that a factory is clearest in production code because the intent is explicit.

### The descriptor protocol

A descriptor is any object whose class defines `__get__`, `__set__` or `__delete__`. When such an object is stored as a **class attribute**, attribute access on instances is routed through those methods. There are two kinds:

- **Data descriptor:** defines `__set__` or `__delete__` (usually both). It takes priority over the instance `__dict__`.
- **Non-data descriptor:** defines only `__get__`. The instance `__dict__` takes priority over it.

`__set_name__(self, owner, name)` is called once when the owning class is created, so a descriptor can learn the attribute name it was assigned to. Here is a reusable validated field:

```python
class Positive:
    def __set_name__(self, owner, name):
        self.public = name
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:          # accessed on the class itself
            return self
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.public} must be positive, got {value}")
        setattr(obj, self.private, value)

class Order:
    qty = Positive()
    price = Positive()

    def __init__(self, qty, price):
        self.qty = qty
        self.price = price

o = Order(2, 10)
print(o.qty, o.__dict__)
try:
    o.qty = 0
except ValueError as e:
    print(e)
print(type(Order.qty).__name__)
```

```text
2 {'_qty': 2, '_price': 10}
qty must be positive, got 0
Positive
```

The descriptor is shared by all instances, so it must store per-instance state on the instance (here in `_qty`), never on `self`. Storing on `self` is the classic descriptor bug: every instance would share one value.

### Attribute lookup order

For `obj.name`, `type(obj).__getattribute__` (the default `object.__getattribute__`) does the following:

1. Look up `name` on the type through its MRO. If found and it is a **data descriptor**, call its `__get__` and stop.
2. Otherwise check the instance `__dict__` (or slots) and return the value if present.
3. Otherwise if the class attribute is a **non-data descriptor**, call its `__get__`; if it is a plain value, return it.
4. If nothing was found, raise `AttributeError`, which triggers `__getattr__` if the class defines it.

```python
class NonData:
    def __get__(self, obj, t=None):
        return "descriptor"

class Data(NonData):
    def __set__(self, obj, v):
        pass

class C:
    nd = NonData()
    d = Data()

c = C()
c.__dict__["nd"] = "instance"
c.__dict__["d"] = "instance"
print(c.nd, c.d)
```

```text
instance descriptor
```

Assignment goes through the same split: `obj.name = v` calls a data descriptor's `__set__` if the class has one, otherwise writes to the instance dict. Assigning `Class.name = v` replaces the descriptor itself and bypasses `__set__`.

### Built-in descriptors you already use

- **Functions** are non-data descriptors. `instance.method` calls `function.__get__(instance, type)`, which returns a bound method. That is the entire mechanism of `self`, and it is why you can shadow a method by assigning to the instance.
- **`property`** is a data descriptor whose `__set__` raises `AttributeError: property 'v' of 'P' object has no setter` when no setter is given. Reading `Class.prop` returns the property object, not a value.
- **`classmethod` and `staticmethod`** are non-data descriptors whose `__get__` binds the class or returns the raw function.
- **`functools.cached_property`** is a non-data descriptor: on first access it computes the value and stores it in the instance `__dict__` under the same name, so later lookups find the instance value before the descriptor. It therefore needs an instance `__dict__` (it does not work with `__slots__` classes without one).

```python
class Lazy:
    """A minimal cached_property: a non-data descriptor that shadows itself."""
    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__[self.name] = self.fn(obj)
        return value

class Report:
    calls = 0

    @Lazy
    def total(self):
        Report.calls += 1
        return 42

r = Report()
print(r.total, r.total, Report.calls, "total" in r.__dict__)
```

```text
42 42 1 True
```

### `__getattr__` versus `__getattribute__`

`__getattribute__` runs on **every** attribute access; overriding it is powerful and dangerous because any `self.x` inside it recurses unless you delegate with `super().__getattribute__(name)`. `__getattr__` is only a **fallback**, called after normal lookup raises `AttributeError`. Prefer `__getattr__` for lazy or proxy attributes and keep it strict: raise `AttributeError` for names you do not handle, otherwise `hasattr`, `copy`, `pickle` and debuggers misbehave on your proxy.

```python
class Config:
    def __init__(self):
        self.known = 1

    def __getattr__(self, name):
        print("fallback", name)
        return f"<missing {name}>"

c = Config()
print(c.known)
print(c.unknown)
```

```text
1
fallback unknown
<missing unknown>
```

Special methods such as `__len__` or `__enter__` are looked up on the **type**, not the instance, so defining them with `__getattr__` or by assigning to an instance has no effect on `len(obj)` or `with obj:`.

## Practical Backend Scenario

An agent framework registers one callable per tool name in a loop: `for name in TOOLS: registry[name] = lambda args: dispatch(name, args)`. In staging everything passes because the test only uses the last tool. In production, every tool call is dispatched to the final tool in the list, because all the lambdas share the loop variable's cell. The fix is a factory (`def bind(name): return lambda args: dispatch(name, args)`) or `functools.partial(dispatch, name)`. The same service also exposes request settings such as `temperature` and `max_tokens` on a config object; a descriptor with `__set_name__` validates ranges once and is reused across fields, instead of a dozen copy-pasted `@property` pairs. When someone later stores a value via `obj.__dict__["temperature"] = 5`, the data descriptor still wins on read, which is why data descriptors are the right tool for invariants.

## Practice Loop

1. Reproduce `UnboundLocalError` with a counter, fix it once with `global` and once by moving the state into a class, and note which one you would ship.
2. Build a loop that creates callbacks in three different ways (naive, default argument, factory) and inspect `__closure__[0].cell_contents` for each.
3. Write the `Positive` descriptor above, use it on two classes, and confirm each instance keeps its own value. Then deliberately store the value on `self` and watch the instances collide.
4. Print `type(Svc.__dict__["run"])`, call `Svc.run.__get__(obj)`, and show that it equals `obj.run`.
5. Implement `Lazy` (a minimal `cached_property`), then turn it into a data descriptor by adding `__set__` and observe why the caching stops working.
6. Add `__getattribute__` logging to a class and list every attribute access made by `print(obj.method())`.

## Evidence of Understanding

- I can predict where each name in a nested function resolves, and explain why `counter += 1` fails without `global` or `nonlocal`.
- I can explain that a closure captures a cell, show it with `__closure__`, and give three fixes for late binding.
- I can state the attribute lookup order and why data descriptors beat the instance dict while non-data descriptors lose to it.
- I can describe how functions become bound methods and how `property`, `classmethod`, `staticmethod` and `cached_property` are built on the protocol.
- I can write a reusable validating descriptor with `__set_name__` that stores state correctly per instance.
- I can choose between `__getattr__` and `__getattribute__` and name the recursion trap.

## Interview Questions to Rehearse

### Q: Why does a list of lambdas created in a loop all return the last value?

Each lambda closes over the variable `i`, not its value at creation time, and all of them share one cell because the loop reuses the same function-level variable. They run after the loop ends, so they see the final value. Fix by binding at creation (`lambda i=i: i` or `functools.partial`) or by calling a factory function that gives each closure its own scope.

### Q: What is the difference between a data and a non-data descriptor?

A data descriptor defines `__set__` or `__delete__` in addition to `__get__`, so it takes precedence over the instance `__dict__` on both reads and writes. A non-data descriptor defines only `__get__`, so an entry in the instance `__dict__` overrides it. Functions are non-data (you can shadow a method per instance); `property` is data (you cannot bypass it by writing to the instance dict). `cached_property` relies on being non-data so its cached value shadows it.

### Q: Walk me through `obj.attr` in CPython.

`type(obj).__getattribute__` is called. It searches the MRO of the type for `attr`. A data descriptor wins immediately. Otherwise the instance `__dict__` is checked, then a non-data descriptor or plain class attribute is used. If everything fails it raises `AttributeError`, and the `__getattr__` hook runs only then. Special-method lookups skip the instance and go directly to the type.

### Q: How does `property` work, and why does `Class.prop` return a property object?

`property` is a data descriptor whose `__get__` calls `fget(instance)`. When the instance argument is `None` (access through the class), `__get__` returns the property itself, which lets tools such as dataclasses, Sphinx and ORMs introspect it. Without a setter, `__set__` raises `AttributeError`, so the attribute is effectively read-only.

### Q: What is `__set_name__` for?

It is called when the owner class is built, with the owner and the attribute name. A descriptor can then derive its storage name or error messages without the user repeating the name. Descriptors used in ORMs and validation libraries rely on it. It is not called if you attach the descriptor to an existing class afterwards, so call it yourself in that case.

### Q: When would you override `__getattribute__` instead of `__getattr__`?

Almost never. `__getattribute__` intercepts every access, including your own, and is easy to recurse on or slow down. It is justified for transparent proxies or tracing tools where you need to intercept existing attributes. For lazy or dynamic fallbacks use `__getattr__`, and always raise `AttributeError` for unknown names.

## Common Pitfalls

- Closures created in loops that all see the final loop value; also `def` inside a `for` loop registering handlers by name.
- Expecting `global` or `nonlocal` to be required for mutation; they are needed only for rebinding.
- Assuming a class variable is visible by bare name inside a method or a nested comprehension.
- Storing per-instance data on the descriptor (`self.value = ...`), which is shared by every instance.
- Forgetting `if obj is None: return self` in `__get__`, which breaks introspection like `Order.qty`.
- Overriding `__getattr__` to return a default for every name, which breaks `hasattr`, `copy`, `pickle` and mocking.
- Calling `self.something` inside `__getattribute__` and recursing infinitely.
- Using `cached_property` on a `__slots__` class without a `__dict__`, or on a value that must be invalidated.

## Suggested Extension

Implement a small `Field` descriptor family (`Typed`, `Ranged`, `NonEmpty`) with a shared base class that uses `__set_name__`, stores values in the instance dict under a private name, and collects all violations into one `ValueError` when you assign several fields in `__init__`. Then show how Pydantic or dataclasses solve the same problem at class-creation time instead of at attribute-access time, and compare the trade-offs.
