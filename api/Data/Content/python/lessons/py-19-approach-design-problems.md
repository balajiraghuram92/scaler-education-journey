# How to Approach Design Problems

Most candidates who fail a low-level design round do not fail on Python. They fail on process: they start typing before they know what is being asked, model the wrong things, and run out of time with half a system that cannot run. A repeatable approach beats any single pattern. This lesson gives you that approach, using a Pen as the warm-up problem, and sets up the machine-coding lessons that follow.

## Concepts Covered

### Three kinds of LLD interview

"Low-level design" is an umbrella for three different formats, and the first thing to do in any loop is to know which one you are in.

| Format | Typical duration | What you deliver | Who uses it |
|---|---|---|---|
| Theory | 30-50 minutes | Answers on OOP, SOLID and patterns; little or no code | Older product companies |
| Design | about 60 minutes | Requirements, class diagram, schema; code optional | Large-scale product companies |
| Machine coding | 2.5-3 hours at the long end, 90 minutes is common | Requirements, diagram, schema, then **running** code for at least one feature end to end | Fintech and consumer-app companies |

In a machine-coding round the interviewer runs your code and then asks follow-ups such as "how would you add a new fee rule". The deliverable is working, extensible code, not slides.

### The six-step approach

1. Receive the one-line problem statement ("design a parking lot").
2. Align on scope with the interviewer.
3. Gather and clarify requirements.
4. Draw the class diagram.
5. Design the schema if state is persisted.
6. Write end-to-end working code, smallest classes first.

Steps 2 and 3 take five to seven minutes and are the cheapest minutes you will spend.

### Align first, then gather requirements

Step zero is a short alignment conversation with three questions. Are we designing an **entity** (a pen) or an **application** (a booking system)? Does anything need to **persist**, or is in-memory fine? How will a user **interact**: hard-coded calls, a command line, or REST? If you know the system, state your understanding and let the interviewer correct it; if not, ask them to describe it.

Then gather requirements under four rules. Do not go overboard. Do not ask "what are the requirements"; **suggest** them and let the interviewer accept or reject. Think about how the system will evolve so your design has seams where change will land. Settle on **five to eight core features** and park the rest explicitly as version 2.

Think from outside to inside and from generic to specific. For a pen, the outside view is "it writes, opens and closes, and can be refilled"; the inside view is a nib, a body, a refill or ink, and a closure.

### Finding entities by noun spotting

Underline the nouns and verbs in the agreed requirements. A noun with its own attributes and behaviour becomes a class; a noun that is just a value on another thing becomes an attribute or an enum; a verb becomes a method on the class that owns the data it needs. For the pen, `Pen`, `Nib`, `Refill` and `Closure` are classes, `BodyMaterial` is an enum, and `write`, `open` and `replace_refill` are behaviours.

Draw the diagram before the code, in text if you are on a plain editor:

```text
            +------------------+        +-----------+
            |  Pen (abstract)  |<>----->|   Nib     |
            |------------------|        +-----------+
            | body: Material   |        +-----------+
            | write(text)      |<>----->|  Refill   |
            | replace_refill() |        | ink_color |
            +--------+---------+        | ink_units |
              ^      ^                  +-----------+
              |      |                  +------------------+
          BallPen  GelPen    <>-------->| Closure (strat.) |
                                        +--------+---------+
                                           ^            ^
                                      CapClosure   ClickClosure
```

### Choosing patterns on purpose

Pick a pattern only when a requirement demands the flexibility. "Cap or clickable" would multiply subclasses (`CapBallPen`, `ClickGelPen`) under inheritance, so it becomes a **Strategy**: the pen has a `Closure`. Ball versus gel really is is-a with different ink behaviour, so those stay subclasses. A **Builder** earns its place when construction has many validated parts; a four-argument pen does not need one.

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class BodyMaterial(Enum):
    PLASTIC = "plastic"
    METAL = "metal"


class OutOfInkError(Exception):
    """Raised when a pen is asked to write with an empty refill."""


class PenNotOpenError(Exception):
    """Raised when writing with a capped or retracted pen."""


@dataclass(frozen=True)
class Nib:
    size_mm: float


@dataclass
class Refill:
    ink_color: str
    ink_units: int

    def consume(self, units: int) -> None:
        if units > self.ink_units:
            raise OutOfInkError(f"needed {units} units, only {self.ink_units} left")
        self.ink_units -= units


class Closure(ABC):
    """Strategy: how a pen opens and closes."""

    def __init__(self) -> None:
        self.is_open = False

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...


class CapClosure(Closure):
    def open(self) -> None:
        self.is_open = True        # pull the cap off

    def close(self) -> None:
        self.is_open = False       # push the cap on


class ClickClosure(Closure):
    def open(self) -> None:
        self.is_open = True        # click: tip extends

    def close(self) -> None:
        self.is_open = False       # click again: tip retracts


class Pen(ABC):
    UNITS_PER_CHAR = 1

    def __init__(self, nib: Nib, body: BodyMaterial, refill: Refill, closure: Closure) -> None:
        self.nib, self.body, self.refill, self.closure = nib, body, refill, closure

    def write(self, text: str) -> str:
        if not self.closure.is_open:
            raise PenNotOpenError("open the pen first")
        self.refill.consume(len(text) * self.UNITS_PER_CHAR)
        return f"[{self.refill.ink_color}] {text}"

    @abstractmethod
    def kind(self) -> str: ...


class BallPen(Pen):
    def kind(self) -> str:
        return "ball"


class GelPen(Pen):
    UNITS_PER_CHAR = 2

    def kind(self) -> str:
        return "gel"


pen = GelPen(Nib(0.5), BodyMaterial.METAL, Refill("blue", 12), ClickClosure())
try:
    pen.write("hi")
except PenNotOpenError as exc:
    print("error:", exc)
pen.closure.open()
print(pen.write("hello"))
try:
    pen.write("a long sentence")
except OutOfInkError as exc:
    print("error:", exc)
```

```text
error: open the pen first
[blue] hello
error: needed 30 units, only 2 left
```

Named exceptions such as `OutOfInkError` are a grading signal; `Exception("bad")` tells the reader nothing.

### Schema design from the class diagram

If the problem persists state, convert the diagram mechanically: each class becomes a table, primitive attributes become columns, and non-primitive attributes become relationships, with the foreign key on the "many" side. Enums become a constrained column or a lookup table.

```sql
CREATE TABLE pens (
    id       INTEGER PRIMARY KEY,
    kind     TEXT NOT NULL CHECK (kind IN ('BALL', 'GEL')),
    closure  TEXT NOT NULL CHECK (closure IN ('CAP', 'CLICK')),
    body     TEXT NOT NULL,
    nib_mm   REAL NOT NULL
);
CREATE TABLE refills (
    id         INTEGER PRIMARY KEY,
    pen_id     INTEGER NOT NULL REFERENCES pens(id),
    ink_color  TEXT NOT NULL,
    ink_units  INTEGER NOT NULL CHECK (ink_units >= 0)
);
```

Run against SQLite with `PRAGMA foreign_keys = ON`, a join returns `[('GEL', 'blue', 12)]` and a refill for a missing pen fails with `FOREIGN KEY constraint failed`.

### Controller, service, repository, and DTOs

The standard shape is three layers. The **controller** is the entry point, like a hotel reception desk: it unwraps the request DTO, calls the service, and wraps a response DTO, doing no real work. The **service** holds business rules and takes plain values, not DTOs. The **repository** only saves and finds. DTOs decouple the outside shape from your models.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class PenKind(Enum):
    BALL = "ball"
    GEL = "gel"


@dataclass(frozen=True)
class AddPenRequest:
    kind: str
    nib_mm: float
    ink_color: str
    ink_units: int
    click: bool


@dataclass(frozen=True)
class AddPenResponse:
    ok: bool
    pen_id: int | None = None
    error: str | None = None


class PenRepository(Protocol):
    def save(self, pen: Pen) -> int: ...
    def find(self, pen_id: int) -> Pen | None: ...


class InMemoryPenRepository:
    def __init__(self) -> None:
        self._pens: dict[int, Pen] = {}

    def save(self, pen: Pen) -> int:
        pen_id = len(self._pens) + 1
        self._pens[pen_id] = pen
        return pen_id

    def find(self, pen_id: int) -> Pen | None:
        return self._pens.get(pen_id)


class PenService:
    def __init__(self, repo: PenRepository) -> None:
        self._repo = repo

    def add_pen(self, kind: PenKind, nib_mm: float, ink_color: str,
                ink_units: int, click: bool) -> int:
        if ink_units <= 0:
            raise ValueError("a new pen needs ink")
        closure = ClickClosure() if click else CapClosure()
        pen_cls = {PenKind.BALL: BallPen, PenKind.GEL: GelPen}[kind]
        pen = pen_cls(Nib(nib_mm), BodyMaterial.PLASTIC, Refill(ink_color, ink_units), closure)
        return self._repo.save(pen)


class PenController:
    def __init__(self, service: PenService) -> None:
        self._service = service

    def add_pen(self, req: AddPenRequest) -> AddPenResponse:
        try:
            pen_id = self._service.add_pen(
                PenKind(req.kind), req.nib_mm, req.ink_color, req.ink_units, req.click
            )
            return AddPenResponse(ok=True, pen_id=pen_id)
        except (ValueError, KeyError) as exc:
            return AddPenResponse(ok=False, error=str(exc))


controller = PenController(PenService(InMemoryPenRepository()))
print(controller.add_pen(AddPenRequest("gel", 0.7, "black", 40, click=True)))
print(controller.add_pen(AddPenRequest("quill", 0.7, "black", 40, click=False)))
print(controller.add_pen(AddPenRequest("ball", 0.7, "red", 0, click=False)))
```

```text
AddPenResponse(ok=True, pen_id=1, error=None)
AddPenResponse(ok=False, pen_id=None, error="'quill' is not a valid PenKind")
AddPenResponse(ok=False, pen_id=None, error='a new pen needs ink')
```

The service never imports a DTO, and swapping the in-memory repository for a database one changes nothing above it.

### Time-boxing a 90-minute round

Budget the clock before you touch the keyboard, and say your plan aloud.

| Minutes | Activity | Exit check |
|---|---|---|
| 0-10 | Align, requirements, MVP versus later | Five to eight features agreed |
| 10-20 | Entities and class diagram, patterns named | Every requirement maps to a box or a line |
| 20-25 | Schema, if persistence was agreed | Foreign keys on the "many" side |
| 25-75 | Code: enums and models, then strategies, repositories, services, controller | Something runs after each stage |
| 75-90 | Tests, one end-to-end demo, follow-up discussion | Demo prints the expected result |

Build leaves before roots: classes that import nothing first, orchestrators late, the entry point last. A stub that raises `NotImplementedError` keeps the import chain alive. Run something after every stage.

### What interviewers grade

- **Extensibility:** a new rule is a new class, not a new `if` in an old one.
- **Correctness:** it runs and matches the requirements you agreed, including the unhappy paths.
- **Tests:** a few fast tests that pin behaviour, using fakes rather than a real database.
- **Naming and structure:** nouns for classes, verbs for methods, enums over magic strings, type hints on every signature.

```python
import pytest


def make_service() -> PenService:
    return PenService(InMemoryPenRepository())


def test_add_pen_assigns_incrementing_ids() -> None:
    service = make_service()
    first = service.add_pen(PenKind.BALL, 0.7, "blue", 10, click=False)
    second = service.add_pen(PenKind.GEL, 0.5, "black", 10, click=True)
    assert (first, second) == (1, 2)


def test_pen_without_ink_is_rejected() -> None:
    with pytest.raises(ValueError):
        make_service().add_pen(PenKind.BALL, 0.7, "blue", 0, click=False)


def test_closed_pen_cannot_write() -> None:
    repo = InMemoryPenRepository()
    pen_id = PenService(repo).add_pen(PenKind.GEL, 0.5, "blue", 20, click=True)
    pen = repo.find(pen_id)
    assert pen is not None
    with pytest.raises(PenNotOpenError):
        pen.write("hi")
    pen.closure.open()
    assert pen.write("hi") == "[blue] hi"
    assert pen.refill.ink_units == 16
```

All three pass against the code above, with no database and no `input()`: that is what the layering bought you.

## Practical Backend Scenario

A forward-deployed take-home says: "design an LLM request quota system" for a customer sharing one API key across teams. You align (library or service, in-memory or Redis); suggest requirements (per-team limits, daily reset, soft versus hard limits) and park billing as version 2; spot nouns (`Team`, `Quota`, `UsageRecord`, `LimitPolicy`); and choose a Strategy for the limit policy because the customer will ask for a token-bucket variant next quarter. The process that handles a pen handles this.

## Practice Loop

1. Take the one-line statement "Design a vending machine". Spend five minutes writing the alignment questions and eight suggested requirements, marking two of them version 2.
2. Underline the nouns in your requirements and sort them into classes, attributes and enums. Draw the class diagram in a `text` fence.
3. Decide where a Strategy is justified (for example payment type or dispensing policy) and where plain inheritance is enough. Write one sentence of justification for each.
4. Code the leaves first: enums, models and exceptions. Run a three-line script that builds them after each stage.
5. Add a repository, a service that takes plain values, and a controller that unwraps and wraps DTOs. Write three tests that need no I/O.
6. Re-run the whole exercise with a stopwatch at 90 minutes and note which step overran.

## Evidence of Understanding

- I can name the three LLD interview formats and say what is delivered in each.
- I can list the six steps and the three alignment questions without notes.
- I can explain why requirements are suggested rather than asked for, and why five to eight is the target.
- I can turn a requirements paragraph into classes, attributes, enums and methods by noun and verb spotting.
- I can justify Strategy over inheritance for one concrete variation, and say when a Builder is overkill.
- I can state the responsibilities of controller, service and repository, and why the service takes plain values.
- I can describe how I would split ninety minutes and what "done" looks like at each checkpoint.

## Interview Questions to Rehearse

### Q: You are given a one-line problem. What do you do in the first ten minutes?

I do not write code. I align on scope (entity or application, persistence, interaction), propose five to eight core requirements from the outside in, mark what is version 2, and ask the interviewer to confirm. The goal is a shared contract I can point at later.

### Q: How do you decide what becomes a class?

Nouns that carry their own attributes and behaviour become classes; values that merely describe something become attributes, and fixed choices become enums. Verbs become methods on the class that owns the data. Then I check every requirement maps to a box or line, and every box has a requirement behind it.

### Q: When is a design pattern the wrong answer?

When no requirement demands the flexibility. A Builder for a three-argument constructor is ceremony; a Strategy with no foreseeable second implementation is indirection. I introduce a pattern when I can name the second variant, and I say it aloud. Over-engineering is a graded failure.

### Q: Why controller, service, and repository for a ninety-minute exercise?

Because each layer has one reason to change and is replaceable in a test: the controller adapts transport, the service owns rules, the repository owns storage. I can swap the store without touching rules and test rules with no I/O. I keep it thin, three small classes per feature, not a framework.

### Q: What if you are running out of time?

I cut scope, not quality. I announce what I am dropping, keep the end-to-end path working, and leave a stub that raises `NotImplementedError`. A smaller system that runs and has tests beats a larger one that does not start.

## Common Pitfalls

- Coding before alignment, then learning the requirement was a REST API, not a console program.
- Asking for requirements instead of proposing them.
- Modelling every noun as a class, including values that are just fields.
- Using inheritance for freely combining variation (cap-or-click times ball-or-gel).
- Building the hardest part first and having nothing runnable at minute forty.
- Business logic in the controller, or `input()` and `print()` deep inside models.
- Magic strings instead of enums, and `Exception("bad")` instead of a named exception.
- Skipping tests because "there was no time", when three small tests take five minutes.

## Suggested Extension

Extend the pen model with a `FountainPen` whose ink comes from a refillable reservoir instead of a replaceable `Refill`. Decide, and justify aloud, whether that is a new subclass, a new strategy, or a change to the `Refill` abstraction. Then add a `PenFactory` and say, in two sentences, whether it is justified at your current scale.
