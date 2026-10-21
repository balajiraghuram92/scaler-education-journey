# ABCs, Protocols and Mixins

In an AI platform you integrate with providers you do not control: payment gateways, ETA vendors, LLM clients, fraud scanners. Python gives you three tools to describe what those integrations must look like, and each fails differently. An abstract base class fails loudly at instantiation, a Protocol fails only when a type checker looks, and a mixin fails silently when its place in the MRO is wrong. Senior interviews probe whether you can choose between them and explain what each one actually enforces at runtime.

## Concepts Covered

### Nominal versus structural typing

An **ABC** is nominal: a class conforms because it declares the relationship, by inheriting or by registering. A **Protocol** is structural: a class conforms because it has the required members, whatever it inherits from. That single difference decides who can satisfy your contract. A vendor SDK you cannot edit can never inherit your ABC, but it can match your Protocol.

| | `abc.ABC` | `typing.Protocol` |
|---|---|---|
| Conformance | declared (inherit or `register`) | shape of the object |
| Enforcement | `TypeError` when instantiating an incomplete class | type checker; optional runtime name check |
| Shares code with implementers | yes (concrete methods, template methods) | no, other than explicit subclassing |
| Best for | your own plug-in hierarchy | boundaries with code you do not own |

### ABCs: what is enforced and when

`ABCMeta` collects the names marked `@abstractmethod` into `__abstractmethods__`. The check happens when you **instantiate**, not when you define the class, and it only checks names.

```python
from abc import ABC, abstractmethod

class Gateway(ABC):
    @abstractmethod
    def charge(self, amount: int) -> str: ...
    @abstractmethod
    def refund(self, amount: int) -> str: ...

class Stripe(Gateway):
    def charge(self, amount: int) -> str:
        return f"charged {amount}"

try:
    Stripe()
except TypeError as e:
    print(e)

class Sloppy(Gateway):
    def charge(self): return "no amount parameter"     # wrong signature, accepted
    def refund(self, a, b, c): return "x"

print(Sloppy().charge())
```

```text
Can't instantiate abstract class Stripe without an implementation for abstract method 'refund'
no amount parameter
```

Three details worth knowing. A subclass that implements all abstract names satisfies the contract for its own subclasses too (`StripeV2(Stripe)` is instantiable). Signatures are never checked at runtime, so use a type checker for that. And an abstract method may have a body that subclasses reach through `super()`, which makes it a template hook. The standard library ships the pattern: subclass `collections.abc.Mapping`, implement `__getitem__`, `__iter__` and `__len__`, and you inherit working `get`, `items`, `keys`, `__contains__` and `__eq__`. Classes can also join an ABC without inheriting: `Closeable.register(Legacy)` makes `isinstance` true (a "virtual subclass"), and `__subclasshook__` lets an ABC define its own structural test, which is how `collections.abc.Iterable` recognises any class with `__iter__`.

### Protocols and what `runtime_checkable` really checks

A Protocol states a shape. Without the decorator, `isinstance` against it raises `TypeError`. With `@runtime_checkable`, `isinstance` checks only that the **names exist**, never signatures or types.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ETAProvider(Protocol):
    def estimate_minutes(self, origin: str, destination: str) -> float: ...

class VendorMapETA:                       # does not inherit anything
    def estimate_minutes(self, origin, destination): return 42.0

class Wrong:
    def estimate_minutes(self): return 1.0    # wrong arity

def get_eta(p: ETAProvider, a: str, b: str) -> float:
    if not isinstance(p, ETAProvider):
        raise TypeError("provider does not implement ETAProvider")
    return p.estimate_minutes(a, b)

print(isinstance(VendorMapETA(), ETAProvider), isinstance(Wrong(), ETAProvider))  # True True
print(get_eta(VendorMapETA(), "Airport", "HSR"))                                   # 42.0
```

The `Wrong` instance passes the runtime check and then fails with a `TypeError` at the call, so runtime checks are a guard rail, and the real contract lives in mypy or pyright. Further details interviewers like: `issubclass()` is rejected for protocols with data members (`name: str`); since 3.12 the check uses static attribute lookup, so it no longer triggers properties or `__getattr__`; protocols cannot be instantiated; and 3.13 adds `typing.get_protocol_members` and `typing.is_protocol` for introspection. A rule of thumb: ABC for hierarchies you own and want to share code in, Protocol at the seams, and `isinstance` against a Protocol sparingly, since the cost and the false confidence both add up.

### Self-registration with `__init_subclass__`

`__init_subclass__` is a hook on the parent class that Python calls **when a subclass is defined**, at class-creation time, not per instance. Class keywords in the `class` statement are passed to it. This replaces most metaclass use for plug-in registries.

```python
from abc import ABC, abstractmethod
from typing import ClassVar

class PaymentGateway(ABC):
    registry: ClassVar[dict[str, type["PaymentGateway"]]] = {}

    def __init_subclass__(cls, *, gateway_name: str | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if gateway_name is None:
            return                                   # helper or intermediate class
        if gateway_name in PaymentGateway.registry:
            raise TypeError(f"duplicate gateway {gateway_name!r}")
        PaymentGateway.registry[gateway_name] = cls

    @abstractmethod
    def charge(self, amount: int) -> str: ...

class Razorpay(PaymentGateway, gateway_name="razorpay"):
    def charge(self, amount): return f"rzp:{amount}"

class Paytm(PaymentGateway):                         # forgot the keyword
    def charge(self, amount): return f"paytm:{amount}"

print(sorted(PaymentGateway.registry))   # ['razorpay']  Paytm is silently missing
```

The "if no name, skip" guard exists so abstract intermediates do not need a name, but it is also why a forgotten keyword fails silently. If every concrete gateway must register, check that in a test, or raise when a class that is not abstract has no name. Always call `super().__init_subclass__(**kwargs)` so sibling hooks in a multiple-inheritance chain still run, and remember a registry only sees classes whose modules have been **imported**.

### Mixins: small capabilities, not identities

A mixin adds one narrow capability (logging, JSON export, audit trail) and is never instantiated alone. It is not an "is-a" relationship. Rules that keep mixins safe: list them **before** the main base so their overrides win and their `super()` calls reach it, give them no required state beyond what they set themselves, accept and forward `**kwargs` in `__init__`, and keep them free of overlapping method names. `class RGW(PaymentGateway, LoggingMixin, JSONMixin)` resolves `describe()` from `PaymentGateway` first because it is first in the MRO; mixins do not automatically win.

```python
from typing import Protocol, runtime_checkable

class LoggingMixin:
    def log_action(self, action: str) -> None:
        print(f"[LOG] {type(self).__name__}: {action}")

class AuditMixin:
    def __init__(self, **kwargs) -> None:
        self.audit_trail: list[str] = []
        super().__init__(**kwargs)

    def record_audit(self, event: str) -> None:
        self.audit_trail.append(event)

@runtime_checkable
class Auditable(Protocol):
    def record_audit(self, event: str) -> None: ...

class PhonePe(LoggingMixin, AuditMixin, PaymentGateway, gateway_name="phonepe"):
    def charge(self, amount: int) -> str:
        self.log_action(f"charge {amount}")
        self.record_audit(f"charged {amount}")
        return "ok"

g = PhonePe()
g.charge(100)
print(g.audit_trail, isinstance(g, Auditable))
```

```text
[LOG] PhonePe: charge 100
['charged 100'] True
```

Here the ABC controls identity and registration, the mixins add capabilities, and a Protocol lets any object with `record_audit`, including a vendor class, be audited. When a mixin needs real state or collaborators, make it a component injected through the constructor.

## Practical Backend Scenario

Your FDE team onboards a bank that already runs an in-house fraud scanner and a third-party ETA service. You define `FraudChecker(ABC)` and ask them to subclass it; their vendor class cannot, and a wrapper would double the surface area to maintain. Rewriting the contract as a `@runtime_checkable` Protocol lets their objects plug in unchanged, while your own checkers still inherit a shared ABC for logging and retries. You pin the boundary with mypy, add an `isinstance` guard at the one place a plug-in is loaded from config, and register each internal gateway through `__init_subclass__` so a new provider needs one file and no edits to a factory.

## Practice Loop

1. Write a `NotificationChannel` ABC with abstract `send` and `get_status` and a `registry` populated by `__init_subclass__(channel_name=...)`. Register `sms`, `email` and `push`.
2. Instantiate an incomplete subclass and read the error. Then write a subclass with wrong signatures and confirm Python accepts it.
3. Define `ETAProvider` as a `runtime_checkable` Protocol and two unrelated implementers. Add a class with the wrong arity and watch the isinstance check pass.
4. Remove the decorator and read the `TypeError`. Add a data member to the Protocol and call `issubclass`.
5. Build `LoggingMixin`, `AuditMixin` and three gateways, then print the MRO and reorder the bases to see what changes.
6. Add a duplicate-name guard to the registry and a test that fails if a concrete gateway is not registered.

## Evidence of Understanding

- You can explain which of ABC and Protocol a vendor class can satisfy and why.
- You can state exactly what `@abstractmethod` and `@runtime_checkable` check, and what they do not.
- You can say when `__init_subclass__` runs and why a missing keyword leaves a silent gap.
- You can order mixin bases deliberately and justify it from the MRO.

## Interview Questions to Rehearse

### Q: ABC or Protocol for a plug-in interface?
ABC when you own the implementations and want shared behaviour, registration and a hard failure on instantiation. Protocol when implementers come from code you do not control, or you want structural, decoupled contracts checked statically. Many systems use both: an ABC for internal base classes and a Protocol at the boundary.

### Q: Does `@abstractmethod` check signatures?
No. It only records names, and enforcement happens at instantiation. A subclass with a different signature is accepted; use mypy or pyright for signature compatibility, and tests for behaviour.

### Q: What does `isinstance(obj, SomeProtocol)` verify?
Only that the object has attributes with the protocol's method names, and it requires `@runtime_checkable`. It does not check arity, types or return values, and `issubclass` is refused for protocols with data members. Since 3.12 the lookup is static, so properties are not executed.

### Q: When does `__init_subclass__` run, and what are its failure modes?
When a subclass is created, before any instance exists, with the class keywords as arguments. Failure modes are forgetting to call `super().__init_subclass__(**kwargs)`, silently skipping classes without a key, overwriting duplicate keys, and relying on registration for modules that were never imported.

### Q: How do mixins interact with the MRO?
Bases are searched left to right, so a mixin listed before the main class overrides it and calls `super()` into it, while one listed after is shadowed. Mixins should be cooperative, small and non-overlapping. If two bases define the same method, the leftmost wins silently.

## Common Pitfalls

- Treating `isinstance(x, Protocol)` as a contract test; it checks names only.
- Expecting an ABC to reject a bad subclass at definition time; it fails only at instantiation.
- Listing a mixin after the main base and wondering why its override never runs.
- A registry keyed by a string that is silently overwritten, or skipped because the keyword was omitted.
- Mixins that hold state or define `__init__` without `**kwargs`, which break any class that combines them.
- Using `ABC.register` or a permissive `__subclasshook__` and then assuming methods exist.

## Suggested Extension

Replace the string-based registry with entry-point discovery: load plug-ins through `importlib.metadata.entry_points` and verify each one against a Protocol at load time, reporting every plug-in that fails with its missing members.
