# Inheritance, MRO and Polymorphism

Every Python service you will maintain has a class hierarchy someone extended three times too many: a payment gateway with logging and retry mixins, a pricing pipeline with stacked surcharges, a model-client base class with five vendor subclasses. When a mixin silently stops running or a surcharge is applied in the wrong order, the root cause is almost always the method resolution order. Interviewers use `super()` and the MRO to separate people who have read the docs from people who have debugged a diamond in production.

## Concepts Covered

### Attribute lookup and the C3 MRO

When you write `obj.name`, Python searches `type(obj).__mro__` left to right and uses the first class that defines `name` (instance `__dict__` and data descriptors take part too, but the class chain is what you reason about). The MRO is computed once at class creation by **C3 linearization**, which merges the parents' linearizations under three rules: a child comes before its parents, the left-to-right order of the bases in the `class` statement is preserved, and the result is monotonic (a subclass never reorders what its parents already agreed on).

```python
class Vehicle:
    def __init__(self, reg_number, **kwargs):
        self.reg_number = reg_number
        super().__init__(**kwargs)

class ElectricVehicle(Vehicle):
    def __init__(self, battery_kwh, **kwargs):
        self.battery_kwh = battery_kwh
        super().__init__(**kwargs)

    def priority(self):
        return 20

class CommercialVehicle(Vehicle):
    def __init__(self, licence, **kwargs):
        self.licence = licence
        super().__init__(**kwargs)

    def priority(self):
        return 30

class ElectricCab(ElectricVehicle, CommercialVehicle):
    pass

print([c.__name__ for c in ElectricCab.__mro__])
cab = ElectricCab(reg_number="KA01", battery_kwh=75, licence="TAXI")
print(cab.priority())
```

```text
['ElectricCab', 'ElectricVehicle', 'CommercialVehicle', 'Vehicle', 'object']
20
```

`Vehicle` appears once, after both of its children. That is the whole answer to the diamond problem: there is no ambiguity, because there is exactly one linear order. C3 can also fail. If you list a base before its own subclass, no consistent order exists and class creation raises immediately:

```python
class A: ...
class B(A): ...
class C(A, B): ...   # TypeError: Cannot create a consistent method resolution order (MRO) for bases A, B
```

Because the error fires at import time, it is cheap to catch. Subtler is **diamond drift**: adding a new base to one branch of a library hierarchy can change the MRO of every downstream subclass, which is why base-class order in a public class statement is part of your API.

### Cooperative super() and the diamond

`super()` does not mean "my parent". It means "the next class after **this** class in the MRO of `type(self)`". The same line of code in `ElectricVehicle.__init__` therefore calls `Vehicle` for a plain `ElectricVehicle` but calls `CommercialVehicle` for an `ElectricCab`. That is what makes cooperative multiple inheritance work: every class does its own part and forwards the rest. Compare the naive approach, which calls parents by name, with the cooperative one:

```python
class Base:
    def __init__(self): print("Base")
class L(Base):
    def __init__(self): Base.__init__(self); print("L")
class R(Base):
    def __init__(self): Base.__init__(self); print("R")
class J(L, R):
    def __init__(self): L.__init__(self); R.__init__(self); print("J")
J()   # Base, L, Base, R, J  -> Base initialised twice
```

With `super().__init__(**kwargs)` in every class the same diamond prints `Base, R, L, J`: each initialiser runs exactly once, in reverse MRO order. The contract for cooperative methods is strict: every class in the chain must accept `**kwargs`, consume only its own parameters, and forward everything else. The chain ends at `object.__init__`, which rejects leftovers, so a misspelt keyword surfaces as `TypeError: object.__init__() takes exactly one argument`. Two failure modes to know:

- A class that forgets to call `super()` silently cuts off everything after it in the MRO. Nothing raises; the later initialisers just never run.
- Mixing positional-only `__init__` signatures with cooperative ones forces you to introduce adapter classes. If that is happening, the design wants composition.

Method chaining through the MRO is also a legitimate design tool. The next example builds a pricing pipeline where the class statement's base order *is* the order of operations:

```python
class BaseFare:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def calculate_fare(self, km: float) -> float:
        return 10 * km

class SurgeMixin:
    def __init__(self, multiplier: float, **kw):
        self.multiplier = multiplier
        super().__init__(**kw)

    def calculate_fare(self, km: float) -> float:
        return super().calculate_fare(km) * self.multiplier

class BookingFeeMixin:
    def __init__(self, fee: float, **kw):
        self.fee = fee
        super().__init__(**kw)

    def calculate_fare(self, km: float) -> float:
        return super().calculate_fare(km) + self.fee

class SurgeOnFee(SurgeMixin, BookingFeeMixin, BaseFare): ...
class FeeOnSurge(BookingFeeMixin, SurgeMixin, BaseFare): ...

print(SurgeOnFee(multiplier=2, fee=50).calculate_fare(10))   # (100 + 50) * 2
print(FeeOnSurge(multiplier=2, fee=50).calculate_fare(10))   # 100 * 2 + 50
```

```text
300
250
```

Swapping two bases changed the price by 50. Surcharge order that matters should be tested, and if finance cares about it, an explicit list of pricing steps is usually clearer than an MRO.

### Polymorphism without interfaces

Python resolves behaviour by **runtime lookup**, so any object with the right method works: duck typing. The cost is that wrong-object-right-name bugs run silently; an `EmailNotification` with a `start()` method will happily be "dispatched" as a vehicle. Three tools narrow that gap without giving up flexibility:

- `isinstance(x, Vehicle)` respects inheritance, so a subclass passes. `type(x) is Vehicle` does not. Prefer `isinstance` (note `isinstance(True, int)` is `True`, a classic trap).
- `@typing.override` (3.12+) makes a type checker fail when an override no longer matches anything in the base, which catches renamed methods.
- Abstract bases and Protocols (next lesson) turn "has a method called start" into a checked contract.

Python has **no overloading**: the second `def calc` in a class body simply rebinds the name, so the one-argument version vanishes and `calc(5)` raises `TypeError`. When you need type-dependent behaviour, `functools.singledispatch` dispatches at runtime on the type of the first argument, unlike Java overloads, which are chosen at compile time from declared types:

```python
from dataclasses import dataclass
from functools import singledispatch

@dataclass(frozen=True)
class Trip:
    distance_km: float

@singledispatch
def estimate_fare(x) -> float:
    raise NotImplementedError(f"cannot price {type(x).__name__}")

@estimate_fare.register
def _(distance: float) -> float:
    return 15 * distance

@estimate_fare.register
def _(route: str) -> float:
    return {"HSR-AIRPORT": 600, "MG-AIRPORT": 550}.get(route, 0)

@estimate_fare.register
def _(trip: Trip) -> float:
    return 15 * trip.distance_km

print(estimate_fare(10.0), estimate_fare("HSR-AIRPORT"), estimate_fare(Trip(12)))
```

```text
150.0 600 180
```

`estimate_fare(10)` raises `NotImplementedError` because `int` is not `float`; registration is by class, not by numeric tower. For methods, use `singledispatchmethod`.

### Operator overloading and the reflected protocol

Operators are method calls: `a < b` is `type(a).__lt__(a, b)`. A well-behaved binary dunder returns `NotImplemented` (the singleton, not the exception) for types it does not understand. Python then tries the reflected method on the right operand, and only then raises `TypeError`. Defining `__lt__` plus `__eq__` and decorating with `functools.total_ordering` fills in the rest. Defining `__eq__` also sets `__hash__` to `None`, so the class becomes unhashable unless you define a matching hash (covered fully in the data model lesson).

```python
import math
from functools import total_ordering

@total_ordering
class Zone:
    def __init__(self, name: str, area: float) -> None:
        self.name, self._area = name, area

    def area(self) -> float:
        return self._area

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Zone):
            return NotImplemented
        return math.isclose(self.area(), other.area())

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Zone):
            return NotImplemented
        return self.area() < other.area()

    __hash__ = None   # equality by area is a derived value; do not hash mutable geometry

print(sorted([Zone("b", 7), Zone("a", 5)])[0].name)   # a
print(Zone("a", 5) == 5)                               # False, no exception
```

### Inheritance versus composition

Inheritance is for substitutable "is-a" relationships: a `Bike` can stand wherever a `Vehicle` is expected without surprising the caller (Liskov). It is the wrong tool for sharing code. Two traps recur: mutable **class attributes** are shared by every subclass (`surge_zones = []` on a base class is one list for the whole hierarchy), and a subclass that skips `super().__init__()` leaves the parent's attributes unset, producing an `AttributeError` far from the cause. If a subclass is just configuring a different strategy, pass the strategy in (a fare policy object) instead of subclassing.

## Practical Backend Scenario

Your ride-hailing platform prices trips with a base fare plus surge, a corporate discount and tax, implemented as mixins combined per region. A refactor reorders two bases in one regional class. Prices in a whole country shift by a few percent and nothing fails, because every combination is a valid class. The fix is a test per region that asserts `FinalFare.__mro__`, plus a structured log of each pricing step so finance can reconstruct any price. In an interview this is the story behind "tell me about a bug caused by multiple inheritance."

## Practice Loop

1. Build `Vehicle`, `Car`, `Bike` and `Auto` with `calculate_fare` and price a mixed list in one loop. Add `@override`.
2. Build the `ElectricCab` diamond with cooperative `**kwargs` initialisers, print `__mro__`, and prove `Vehicle.__init__` runs once.
3. Break it: remove one `super().__init__(**kwargs)`, then pass a misspelt keyword, and read both failures.
4. Create `class C(A, B)` where `B` subclasses `A` and read the C3 error.
5. Implement `SurgeMixin` and `BookingFeeMixin`, swap their order, and compare prices.
6. Write `estimate_fare` with `singledispatch` for `float`, `str` and a `Trip` class, and try an `int`.
7. Implement `Zone` with `__eq__`, `__lt__` and `__add__`, sort a list, then try a `set`.

## Evidence of Understanding

- You can derive a diamond's MRO by hand with the C3 rules and confirm it with `__mro__`.
- You can explain why one `super()` call can reach different classes for different instances.
- You can name two ways a cooperative chain breaks and the symptom of each.
- You can explain why Python has no overloading and what replaces it.
- You can explain why `__eq__` removes hashability and why `NotImplemented` beats raising.

## Interview Questions to Rehearse

### Q: How does Python decide which method to call in a diamond hierarchy?
It reads `type(obj).__mro__`, the C3 linearization: children before parents, declared base order preserved, each class once. The first class defining the attribute wins, so `ElectricCab(ElectricVehicle, CommercialVehicle)` uses `ElectricVehicle.priority` and `Vehicle` comes last. If no consistent order exists, class creation raises `TypeError`.

### Q: What does `super()` actually do?
It continues the lookup in `type(self).__mro__` just after the class where the call is written. It is not "the parent". Each cooperative method does its work and calls `super()`, and the instance's class decides who runs next. The price is a shared signature, usually `**kwargs`.

### Q: Why might `Vehicle.__init__` run twice, and how do you prevent it?
Calling parents by name (`L.__init__(self)`, `R.__init__(self)`) visits the shared base once per branch. `super().__init__(**kwargs)` in every class visits each class once. The residual risk is a class that forgets to call `super()`, which silently skips everything behind it.

### Q: Does Python support method overloading?
No. A later `def` rebinds the name, so only the last survives. Use defaults, `functools.singledispatch` for runtime dispatch on the first argument, or separate methods. Java overloads are chosen at compile time from declared types.

### Q: What goes wrong if a class defines `__eq__` but not `__hash__`?
Python sets `__hash__` to `None`, so instances cannot go in sets or be dict keys. Equal objects must hash equally, and the inherited identity hash would break that. Define both over the same immutable fields, or stay deliberately unhashable.

### Q: Composition or inheritance for surge, discount and tax?
Inheritance suits a fixed hierarchy of vehicle kinds. For combinable pricing steps prefer an explicit list of step objects, because the MRO makes order implicit and easy to break. If you use mixins, keep them small and pin the MRO in a test.

## Common Pitfalls

- Calling `Parent.__init__(self)` by name, which double-initialises once a second parent appears.
- Omitting `super().__init__()`, then hitting an `AttributeError` far from the cause.
- Writing a mixin `__init__` that does not accept and forward `**kwargs`.
- Assuming the last-listed base wins; the leftmost base is searched first.
- Validating with `type(x) == Vehicle`, or forgetting `bool` is an `int`.
- Defining `__eq__` for ordering and losing hashability or mishandling foreign types.
- Using a mutable class attribute on a base class and mutating it through an instance.

## Suggested Extension

Write `describe_mro(cls)`, which prints each class in the MRO with the methods it defines, and a pytest that fails if `FinalFare.__mro__` changes. Then add `BookingFeeMixin` to one regional class and use the test to see exactly which prices move.
