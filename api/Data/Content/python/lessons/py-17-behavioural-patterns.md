# Behavioural Design Patterns

Creational and structural patterns decide what objects exist and how they connect. Behavioural patterns decide who does what at runtime and how objects talk to each other, which is where backend systems either stay flexible or calcify into `if/elif` forests. In interviews, Strategy and Observer are the high-frequency pair, and senior candidates are expected to follow up with Command, State and Chain of Responsibility, and, more importantly, to say when Python's functions and `Enum`s make the heavyweight class diagram unnecessary.

## Concepts Covered

### Strategy: interchangeable algorithms

The problem is a conditional that selects behaviour: `if mode == "car": ... elif mode == "bike": ...`. It violates Open/Closed (every new mode edits the function) and Single Responsibility (one function knows every algorithm). Strategy extracts each algorithm behind a common interface and lets the caller pick one.

The classic form is an interface plus one class per strategy, with a factory choosing the class. In Python, if a strategy is a single operation, it is just a **callable**. Functions are first-class, so a dict of functions is the strategy registry:

```python
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RideDetails:
    distance_km: float
    minutes: float


PricingStrategy = Callable[[RideDetails], float]      # a strategy is just a callable here
BASE_FARE = 5.0


def distance_based(ride: RideDetails) -> float:
    return BASE_FARE + 2.0 * ride.distance_km

def time_based(ride: RideDetails) -> float:
    return BASE_FARE + 0.5 * ride.minutes

def surge(multiplier: float) -> PricingStrategy:      # parameterised strategy via closure
    def price(ride: RideDetails) -> float:
        return distance_based(ride) * multiplier
    return price


STRATEGIES: dict[str, PricingStrategy] = {
    "distance": distance_based,
    "time": time_based,
    "surge_2x": surge(2.0),
}


def quote(ride: RideDetails, mode: str) -> float:
    try:
        return STRATEGIES[mode](ride)
    except KeyError:
        raise ValueError(f"unknown pricing mode: {mode}") from None


ride = RideDetails(distance_km=10, minutes=20)
print({m: quote(ride, m) for m in STRATEGIES})


class TieredPricing:                                   # class form: state, config, several methods
    def __init__(self, tiers: list[tuple[float, float]]) -> None:   # (up_to_km, rate)
        self._tiers = tiers

    def __call__(self, ride: RideDetails) -> float:
        total, prev = BASE_FARE, 0.0
        for up_to, rate in self._tiers:
            km = max(0.0, min(ride.distance_km, up_to) - prev)
            total += km * rate
            prev = up_to
        return total


STRATEGIES["tiered"] = TieredPricing([(5, 2.0), (float("inf"), 1.5)])
print(quote(ride, "tiered"))
```

```text
{'distance': 25.0, 'time': 15.0, 'surge_2x': 50.0}
22.5
```

Choose a function when the strategy is one stateless operation; choose a class (or a `Protocol` with a class) when the strategy carries configuration, needs several methods, or holds collaborators such as an HTTP client. The registry dict doubles as the factory, and adding a mode touches no existing code. In LLM systems the same idea selects a chunking algorithm, a reranker, or a routing policy per request.

### Observer: decouple the event from its reactions

When an order is placed, the invoice generator, inventory, and email service must all react. If `place_order()` calls each by name, adding a listener edits it every time. Observer inverts that: the **subject** announces, observers **subscribe**, and the subject knows nothing about them beyond a callable shape. The in-process version is an event bus.

```python
from __future__ import annotations
import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

log = logging.getLogger("bus")


@dataclass(frozen=True, slots=True)
class OrderPlaced:
    order_id: str
    total: float


Handler = Callable[[Any], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Handler) -> Callable[[], None]:
        self._handlers[event_type].append(handler)
        def unsubscribe() -> None:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
        return unsubscribe

    def publish(self, event: Any) -> None:
        for handler in list(self._handlers[type(event)]):   # snapshot: safe if a handler unsubscribes
            try:
                handler(event)
            except Exception:                                # one bad observer must not block the rest
                log.exception("handler %r failed for %r", handler, event)


bus = EventBus()
seen: list[str] = []

def invoice(e: OrderPlaced) -> None: seen.append(f"invoice:{e.order_id}")
def broken(e: OrderPlaced) -> None: raise RuntimeError("email service down")
def inventory(e: OrderPlaced) -> None: seen.append(f"stock:{e.order_id}")

bus.subscribe(OrderPlaced, invoice)
bus.subscribe(OrderPlaced, broken)
off = bus.subscribe(OrderPlaced, inventory)

bus.publish(OrderPlaced("o-1", 49.0))
off()
bus.publish(OrderPlaced("o-2", 12.0))
print(seen)
```

```text
['invoice:o-1', 'stock:o-1', 'invoice:o-2']
```

Every detail in `publish` is a production decision. Iterating a **copy** of the handler list prevents "list changed during iteration" when a handler unsubscribes. Catching per-handler exceptions stops one failing email service from silencing inventory. Returning an `unsubscribe` closure avoids the leak where a long-lived bus holds short-lived subscribers forever (for bound methods, `weakref.WeakMethod` is the other defence). Ordering, async handlers, retries and durability are not provided: an in-process bus is a synchronous call list. When the reaction must survive a crash, you need a queue or outbox, which is the same pattern with a durable transport.

> **Interview tip:** Strategy chooses **one** behaviour per call; Observer runs **all** registered reactions for an event. If you can say that sentence, you can answer most "which pattern?" scenario questions on the spot.

### Command: requests as objects, with undo

Command turns an action into an object with `execute()` and, if the action is reversible, `undo()`. That gives you history, redo, queuing, logging and retry. The undo-capable command must capture whatever it needs to reverse itself at execution time.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


@dataclass
class Conversation:
    messages: list[str] = field(default_factory=list)


@dataclass
class AddMessage:
    convo: Conversation
    text: str
    def execute(self) -> None: self.convo.messages.append(self.text)
    def undo(self) -> None: self.convo.messages.pop()


@dataclass
class TrimToLast:                       # n >= 1
    convo: Conversation
    n: int
    _removed: list[str] = field(default_factory=list, init=False)   # captured for undo
    def execute(self) -> None:
        self._removed = self.convo.messages[: -self.n]
        self.convo.messages[:] = self.convo.messages[-self.n:]
    def undo(self) -> None:
        self.convo.messages[:0] = self._removed


class History:
    def __init__(self) -> None:
        self._done: list[Command] = []
        self._undone: list[Command] = []

    def run(self, cmd: Command) -> None:
        cmd.execute()
        self._done.append(cmd)
        self._undone.clear()            # a new action invalidates the redo stack

    def undo(self) -> None:
        if self._done:
            cmd = self._done.pop(); cmd.undo(); self._undone.append(cmd)

    def redo(self) -> None:
        if self._undone:
            cmd = self._undone.pop(); cmd.execute(); self._done.append(cmd)


c, h = Conversation(), History()
for t in ("hi", "what is RAG?", "explain chunking", "thanks"):
    h.run(AddMessage(c, t))
h.run(TrimToLast(c, 2));        print(c.messages)
h.undo();                       print(c.messages)
h.undo(); h.undo();             print(c.messages)
h.redo();                       print(c.messages)
```

```text
['explain chunking', 'thanks']
['hi', 'what is RAG?', 'explain chunking', 'thanks']
['hi', 'what is RAG?']
['hi', 'what is RAG?', 'explain chunking']
```

`TrimToLast` records the removed prefix when it runs, which is what makes `undo` exact. A new command clears the redo stack, as every editor does. Commands that call external systems (send an email, charge a card) cannot truly undo and need a **compensating** command instead, which is the basis of saga-style workflows. In Python, a plain closure pair or `functools.partial` is often enough when you only need deferred execution without undo.

### State: legal transitions as data

An entity whose behaviour depends on its lifecycle (ticket, payment, ingestion job) needs the rule "from X you may only go to Y or Z". The textbook State pattern gives each state a class with its own methods; in Python the most maintainable form for most backends is an `Enum` plus an explicit transition table, so the legal graph is one reviewable literal.

```python
from __future__ import annotations
from enum import Enum, auto


class JobState(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCEEDED = auto()
    FAILED = auto()
    CANCELLED = auto()


ALLOWED: dict[JobState, frozenset[JobState]] = {
    JobState.PENDING: frozenset({JobState.RUNNING, JobState.CANCELLED}),
    JobState.RUNNING: frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}),
    JobState.FAILED: frozenset({JobState.RUNNING}),         # retry
    JobState.SUCCEEDED: frozenset(),                        # terminal
    JobState.CANCELLED: frozenset(),                        # terminal
}


class IllegalTransition(Exception): ...


class IngestionJob:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.state = JobState.PENDING
        self.attempts = 0
        self.history: list[JobState] = [self.state]

    def _go(self, new: JobState) -> None:
        if new not in ALLOWED[self.state]:
            raise IllegalTransition(f"{self.state.name} -> {new.name}")
        self.state = new
        self.history.append(new)

    def start(self) -> None:
        self._go(JobState.RUNNING)
        self.attempts += 1

    def succeed(self) -> None: self._go(JobState.SUCCEEDED)
    def fail(self) -> None: self._go(JobState.FAILED)
    def cancel(self) -> None: self._go(JobState.CANCELLED)


job = IngestionJob("doc-42")
job.start(); job.fail(); job.start(); job.succeed()
print([s.name for s in job.history], job.attempts)
try:
    job.start()
except IllegalTransition as e:
    print("rejected:", e)
```

```text
['PENDING', 'RUNNING', 'FAILED', 'RUNNING', 'SUCCEEDED'] 2
rejected: SUCCEEDED -> RUNNING
```

Move to State classes when each state has substantially different behaviour for many operations. Whichever form you choose, enforce transitions **in the persistence layer too**: a compare-and-set `UPDATE ... WHERE state = :expected` is what stops two workers from both moving a job out of `PENDING`.

### Chain of Responsibility: the middleware pipeline

A request passes through handlers; each may act, pass it on, or **short-circuit**. That is exactly ASGI and Starlette middleware, and the shape for an LLM gateway: authenticate, rate-limit, redact, then call the model. A middleware takes the request and a `next` callable.

```python
from __future__ import annotations
import re
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Request:
    user: str | None
    prompt: str
    meta: dict = field(default_factory=dict)


@dataclass
class Response:
    status: int
    body: str


Next = Callable[[Request], Response]
Middleware = Callable[[Request, Next], Response]


def auth(req: Request, nxt: Next) -> Response:
    if req.user is None:
        return Response(401, "unauthenticated")           # short-circuit: chain stops here
    return nxt(req)


def redact_emails(req: Request, nxt: Next) -> Response:
    req.prompt = re.sub(r"\S+@\S+", "[email]", req.prompt)
    return nxt(req)


def make_rate_limiter(limit: int) -> Middleware:
    counts: dict[str, int] = {}
    def rate_limit(req: Request, nxt: Next) -> Response:
        counts[req.user] = counts.get(req.user, 0) + 1
        if counts[req.user] > limit:
            return Response(429, "slow down")
        return nxt(req)
    return rate_limit


def build_chain(middlewares: list[Middleware], endpoint: Next) -> Next:
    chain = endpoint
    for mw in reversed(middlewares):                      # first in the list ends up outermost
        chain = (lambda mw, nxt: lambda req: mw(req, nxt))(mw, chain)
    return chain


def endpoint(req: Request) -> Response:
    return Response(200, f"model saw: {req.prompt}")


handle = build_chain([auth, make_rate_limiter(2), redact_emails], endpoint)
print(handle(Request(None, "hi")))
print(handle(Request("ann", "mail bob@corp.com")))
print(handle(Request("ann", "again")))
print(handle(Request("ann", "third")))
```

```text
Response(status=401, body='unauthenticated')
Response(status=200, body='model saw: mail [email]')
Response(status=200, body='model saw: again')
Response(status=429, body='slow down')
```

Order matters and is a design statement: `auth` before `rate_limit` keeps anonymous traffic from consuming a user's quota, and the limiter before the model call protects the expensive resource. The `(lambda mw, nxt: ...)` wrapper binds the loop variables immediately; a bare lambda in the loop would capture the *last* middleware for every layer, the late-binding closure bug.

### Choosing between them

| Pattern | Question it answers | Python idiom |
|---|---|---|
| Strategy | Which algorithm, chosen by the caller? | Function or callable in a dict |
| Observer | Who reacts to this event? | Callback list, event bus, signals |
| Command | Can I queue, log, undo this action? | Dataclass with `execute`/`undo` |
| State | What may happen next, given where I am? | `Enum` + transition table |
| Chain of Responsibility | Who handles this request, in what order? | Middleware list with `next` |

> **Pitfall:** Strategy and State look alike (an object delegating to an interchangeable collaborator). The difference is who changes it: the client selects a Strategy, whereas the object itself moves between States as a consequence of events.

## Practical Backend Scenario

You own an LLM gateway used by several product teams. Teams want different routing (cheapest model, lowest latency, highest quality), so routing is a strategy in a registry selected by tenant configuration. Every completed request must fan out to billing, audit logging and an anomaly detector, so the gateway publishes a `CompletionFinished` event and those three subscribe, and a failing audit sink never blocks billing. Auth, quota, PII redaction and prompt-injection screening form a middleware chain whose order was argued in a design review. Long-running fine-tune and ingestion jobs are state machines with a transition table and compare-and-set updates. Operators of an admin console can "revert last config change", implemented as commands with undo.

## Practice Loop

1. Type out the pricing registry. Add a new `"night"` strategy as a function and confirm that no existing code changed. Then rewrite one strategy as a class implementing `__call__` and decide which form you prefer.
2. Run the `EventBus` example. Make a handler unsubscribe itself during `publish` and verify the snapshot copy prevents a bug. Remove the `list(...)` copy and observe what changes.
3. Add `publish_async` that runs coroutine handlers with `asyncio.gather(..., return_exceptions=True)`. Decide and document how failures are reported.
4. Implement `History` with a maximum depth and test undo, redo, and redo invalidation after a new command.
5. Extend `JobState` with `PAUSED`, update the table, and write a parametrised test that checks every state pair against `ALLOWED`.
6. Reorder the middleware list in three ways and write down the observable difference for an anonymous user making 10 requests.

## Evidence of Understanding

- I can state Strategy versus Observer in one sentence each and apply them to a new scenario.
- I can justify using a function, a callable class, or a `Protocol` implementation for a strategy.
- I can list at least four decisions an event bus must make (snapshot, exception isolation, unsubscribe, ordering and durability).
- I can implement undo by capturing state at execute time, and explain why external side effects need compensation.
- I can show a legal-transition table and say where else the rule must be enforced.
- I can build a middleware chain, explain short-circuiting, and explain the loop-closure trap.

## Interview Questions to Rehearse

### Q: Strategy or if/elif? When is the pattern overkill?

An `if/elif` that selects behaviour grows with every case and violates Open/Closed. Strategy moves each algorithm behind one signature and selects it from a registry. It is overkill for two stable branches that never change. In Python, I would pick a plain function in a dict before reaching for an interface and a class per branch.

### Q: How would you implement Observer in a production service?

For in-process reactions, a typed event bus: subscribe returns an unsubscribe handle, publish iterates a snapshot and isolates handler exceptions. I would state clearly that it is synchronous and not durable. If a reaction must not be lost or must not slow the request, I publish to a queue or write to an outbox, and observers consume from it.

### Q: How does undo work in the Command pattern, and what can't it undo?

Each command captures at execution the information needed to reverse itself, and a history keeps done and undone stacks. A new command clears the redo stack. Actions with external side effects (an email sent, a card charged) cannot be undone, so you issue a compensating command (refund, correction email) and accept that the history is of intent.

### Q: Why prefer a transition table for a state machine?

It makes the legal graph a single piece of reviewable data, easy to test exhaustively and to render as a diagram. State classes make sense when per-state behaviour diverges heavily. Either way the database update must be conditional on the expected current state, otherwise concurrent workers can both transition the same entity.

### Q: What is Chain of Responsibility, and where do you meet it in Python backends?

A request flows through ordered handlers, each of which can handle it, modify it and forward it, or end the chain. It is ASGI/Starlette middleware, Django middleware, and the request-processing pipeline of an LLM gateway. Order is a design decision (auth before rate limiting before model call), and the classic bug is building the chain in a loop with late-binding lambdas.

## Common Pitfalls

- Selecting a strategy with an `if` chain inside the factory, which re-creates the coupling you removed.
- Mutating the observer list while iterating it, or letting one handler's exception abort the others.
- Forgetting to unsubscribe, so a long-lived publisher keeps dead subscribers (and their memory) alive.
- Treating an in-process bus as reliable delivery.
- An undo that reconstructs state instead of capturing it, so it is wrong after other commands run.
- Confusing Strategy with State: if the object transitions itself, it is State.
- State changes enforced only in application code, with no conditional update in the database.
- A middleware chain order nobody wrote down, and loop-defined lambdas that bind the wrong middleware.

## Suggested Extension

Add a `retry` middleware and a `cache` middleware to the chain and choose their positions relative to rate limiting and redaction. For at least three different orderings, write a pytest case that asserts a concrete behavioural difference (for example, whether a cached answer counts against the user's quota). Then write down which ordering you would ship and why.
