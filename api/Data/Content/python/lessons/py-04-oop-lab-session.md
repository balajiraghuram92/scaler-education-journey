# OOP Lab: Modelling a Real Domain

Machine-coding rounds and design interviews reward one skill above syntax: taking a vague domain, finding the entities, deciding which behaviour lives where, and choosing the right mechanism for each relationship. This lab builds a small lending library end to end, using every tool from the previous lessons (abstract classes, properties, class attributes, protocols, mixins and dunders) and asks, for each choice, what would break in a larger system.

## Concepts Covered

### From nouns to entities, and who owns the rule

Start by listing nouns and the verbs they own. Here the entities are `User` (with `Member` and `Librarian`), `Book` (with `Novel` and `Textbook`), `Magazine`, `Loan` and `Library`. The design question that decides quality is where **lending policy** lives. If `Book.borrow(member)` owns it, behaviour sits next to its data but the policy ("limit of five, no double lending") is smeared across classes. If `Library.lend(member, book)` owns it, the policy is in one place but the library risks becoming a god object that reaches into everyone's internals. A reasonable resolution: entities expose small intention-revealing methods (`can_borrow()`, `is_available`), and a service class owns the cross-entity rule and raises domain errors.

### Abstract users, read-only identity and class attributes

`User` is abstract: nobody is "just a user", and each role must say how it renders a dashboard and whether it can borrow. The ID comes from a class-level counter shared by every subclass, and it is exposed through a read-only property so it cannot be reassigned.

```python
import itertools
from abc import ABC, abstractmethod

class User(ABC):
    _ids = itertools.count(1)                       # shared by all subclasses
    total_users = 0

    def __init__(self, name: str) -> None:
        self.name = name
        self._user_id = f"U{next(User._ids):03d}"
        User.total_users += 1

    @property
    def user_id(self) -> str:
        return self._user_id

    @abstractmethod
    def display_dashboard(self) -> str: ...
    @abstractmethod
    def can_borrow(self) -> bool: ...

class Member(User):
    MAX_BORROW_LIMIT = 5

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._borrowed = 0

    def can_borrow(self) -> bool:
        return self._borrowed < self.MAX_BORROW_LIMIT

    def increment_borrow(self) -> None:
        self._borrowed += 1

    def decrement_borrow(self) -> None:
        self._borrowed = max(0, self._borrowed - 1)

    def display_dashboard(self) -> str:
        return f"{self.name}: {self._borrowed}/{self.MAX_BORROW_LIMIT} borrowed"

class Librarian(User):
    def __init__(self, name: str, employee_no: int) -> None:
        super().__init__(name)
        self.employee_no = employee_no
    def can_borrow(self) -> bool: return False
    def display_dashboard(self) -> str: return f"{self.name} (staff {self.employee_no})"

a, b, c = Member("Asha"), Member("Bala"), Librarian("Chitra", 77)
print(a.user_id, b.user_id, c.user_id)       # U001 U002 U003
```

Three behaviours follow from this code. Each `super().__init__()` routes to `User.__init__`, so the single shared counter increments once per object whichever subclass is created. Assigning `a.user_id = "X"` raises `AttributeError: property 'user_id' ... has no setter`. And `User("x")` raises `TypeError` because the abstract methods are unimplemented. A concrete subclass of a concrete class (`PremiumMember(Member)`) needs no re-implementation, since `Member` already satisfied the contract.

Class attributes are read through the instance but **written** per instance, which is a classic trap. `Member.MAX_BORROW_LIMIT = 2` takes effect immediately for every member, since `can_borrow` looks the value up at call time. But `a.MAX_BORROW_LIMIT = 9` creates an instance attribute that shadows the class value for `a` only. Likewise `self.counter += 1` on a class attribute reads the class value and writes a new instance attribute, leaving the class counter at zero.

```python
class Member:
    MAX_BORROW_LIMIT = 5

a, b = Member(), Member()
Member.MAX_BORROW_LIMIT = 2
a.MAX_BORROW_LIMIT = 9                      # shadows the class value for `a` only
print(Member.MAX_BORROW_LIMIT, b.MAX_BORROW_LIMIT, a.MAX_BORROW_LIMIT, vars(a))

class Counter:
    n = 0
    def bump(self): self.n += 1               # reads class n, writes instance n

x = Counter(); x.bump(); x.bump()
print(Counter.n, x.n, vars(x))
```

```text
2 2 9 {'MAX_BORROW_LIMIT': 9}
0 2 {'n': 2}
```

### Contracts: nominal for your hierarchy, structural at the edges

Lending requires a real behavioural contract, so `Borrowable` is an ABC. Searching only needs a `matches` method, and a `Magazine` or a third-party `JournalDB` should be searchable without being lendable, so `Searchable` is a `runtime_checkable` Protocol. `isinstance(item, Borrowable)` is a nominal check that a duck-typed `AudioGuide` fails even if it has the same methods; `isinstance(item, Searchable)` is a shape check that it passes.

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol, runtime_checkable

class TimestampedMixin:
    def __init__(self, *args, **kwargs) -> None:
        self.created_at = datetime.now()
        super().__init__(*args, **kwargs)           # keep the chain alive

class Borrowable(ABC):
    is_available: bool
    @abstractmethod
    def title_for_loan(self) -> str: ...

@runtime_checkable
class Searchable(Protocol):
    def matches(self, query: str) -> bool: ...

class Book(TimestampedMixin, Borrowable):
    def __init__(self, isbn: str, title: str, author: str = "") -> None:
        super().__init__()
        self._isbn, self.title, self.author = isbn, title, author
        self.is_available = True

    @property
    def isbn(self) -> str: return self._isbn
    def title_for_loan(self) -> str: return self.title
    def matches(self, query: str) -> bool:
        q = query.lower()
        return q in self.title.lower() or q in self.author.lower()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self._isbn == other._isbn
    def __hash__(self) -> int: return hash(self._isbn)
    def __repr__(self) -> str: return f"Book({self._isbn!r}, {self.title!r})"

class Magazine:                                   # searchable, deliberately not borrowable
    def __init__(self, title: str, issue: str) -> None:
        self.title, self.issue = title, issue
    def matches(self, query: str) -> bool: return query.lower() in self.title.lower()
    def __repr__(self) -> str: return f"Magazine({self.title!r})"
```

`Book`'s MRO is `Book, TimestampedMixin, Borrowable, ABC, object`: the mixin comes first so its `__init__` runs and forwards to the rest. Equality and hash are both by ISBN, so two `Book` objects loaded separately for the same ISBN collapse in a `set`. Define `__eq__` without `__hash__` and `{l1, l2}` raises `TypeError: unhashable type`.

### The service: policy, domain errors and a collection interface

`Library` is a collection (`__len__`, `__iter__`, `__contains__`, `__getitem__`) and a service (`lend`, `return_book`, `search`). Slicing needs no extra code when `__getitem__` delegates to the internal list. `in` works through `__contains__` and is defined over ISBNs here, not objects. Failures use distinct domain exceptions so callers can handle each differently, with built-in `TypeError` reserved for programming errors such as lending a non-borrowable.

```python
class LibraryError(Exception): ...
class ItemUnavailable(LibraryError): ...
class BorrowLimitReached(LibraryError): ...

class Library:
    def __init__(self) -> None:
        self._items: list[object] = []
    def add(self, item: object) -> None: self._items.append(item)
    def __len__(self) -> int: return len(self._items)
    def __iter__(self): return iter(self._items)
    def __contains__(self, isbn: str) -> bool:
        return any(getattr(i, "isbn", None) == isbn for i in self._items)

    def search(self, query: str) -> list[object]:
        return [i for i in self._items if isinstance(i, Searchable) and i.matches(query)]

    def lend(self, member: Member, item: object) -> None:
        if not isinstance(item, Borrowable):
            raise TypeError(f"{type(item).__name__} is not borrowable")
        if not item.is_available:
            raise ItemUnavailable(item.title_for_loan())
        if not member.can_borrow():
            raise BorrowLimitReached(member.name)
        item.is_available = False
        member.increment_borrow()
```

Searching a library holding `Book("N-1", "Dune", "Herbert")` and `Magazine("Dune Monthly", "Jul")` for `"dune"` returns `[Book('N-1', 'Dune'), Magazine('Dune Monthly')]`, and lending the magazine raises `TypeError: Magazine is not borrowable`. Note what the sketch still lacks: lending and the availability check are not atomic, so two web workers could lend the same copy. In a real service the invariant belongs in the database (a unique constraint or `SELECT ... FOR UPDATE`) or behind a lock, a point the concurrency lessons return to.

### Composition and immutability for records

`Loan` relates a member and a book plus a due date. It is a record, not an actor, so a frozen dataclass with `member` and `book` fields is the right fit (`@dataclass(frozen=True)` gives `__eq__`, `__hash__` and `__repr__` for free). Prefer composition (a `Loan` holding references) to inheritance whenever the relationship is "has" or "is related to".

## Practical Backend Scenario

An FDE engagement for a university digitises its catalogue. Staff want to lend books, but also reserve lab equipment and loan out digital licences, and the vendor's existing `JournalDB` search client cannot be modified. The nominal `Borrowable` ABC protects the lending path (only things that implement `title_for_loan` and carry `is_available` can be lent), while a `Searchable` Protocol lets the search page accept the vendor client unchanged. During the pilot a second web worker lends the same copy to two members. The root cause is not the OOP model but the missing atomic update, and the fix is a database-level guard in the repository behind `Library`.

## Practice Loop

1. Build `User`, `Member` and `Librarian`; confirm the ID counter is shared and that `User("x")` fails.
2. Change `Member.MAX_BORROW_LIMIT` at runtime and observe `can_borrow()`. Then assign it on one instance and inspect `vars(member)`.
3. Implement `Borrowable` as an ABC and `Searchable` as a Protocol; show a third-party class passing one and failing the other.
4. Add `TimestampedMixin` to `Book`, print `Book.__mro__`, then delete the `super()` line from the mixin and add a second mixin after it to see that mixin's `__init__` silently skipped.
5. Implement `__eq__`, `__hash__` and `__repr__` on `Book` by ISBN and verify set deduplication.
6. Implement `Library` with `__len__`, `__iter__`, `__contains__`, `__getitem__`; slice it and iterate it twice.
7. Implement `lend` and `return_book` with distinct domain exceptions, then write pytest cases for each failure path.

## Evidence of Understanding

- You can justify where the lending rule lives and name the trade-off against the alternative.
- You can explain how a shared class attribute counter works across subclasses and when assignment shadows it.
- You can say why an ABC rejects a duck-typed class that a Protocol accepts.
- You can order a mixin and the main base deliberately and prove the result from `__mro__`.
- You can explain why a missing `__hash__` makes `Loan` or `Book` unusable in sets.

## Interview Questions to Rehearse

### Q: Where should the lending logic live: `Book.borrow()` or `Library.lend()`?
Keep each entity responsible for its own state (`is_available`, `can_borrow`), and put the rule that spans entities into a service. Pushing it all into `Book` scatters policy, while pushing everything into `Library` creates a god object. I would also add domain exceptions so callers can react to each failure.

### Q: A class-level counter assigns IDs. What can go wrong?
Updating through `self.counter += 1` creates an instance attribute and leaves the class counter unchanged, so use `Class.counter` or `itertools.count`. In multi-threaded or multi-process services a Python counter is not a safe ID source; use the database or a UUID.

### Q: Why does `isinstance(AudioGuide(), Borrowable)` return `False` when the methods match, but a `Searchable` check passes?
`Borrowable` is an ABC and `isinstance` is nominal: the class must inherit or register. `Searchable` is a runtime-checkable Protocol and checks that the member names exist. Choose nominal checks for contracts you control and structural ones for third-party objects.

### Q: How do you make a property read-only, and what happens on assignment?
Expose the value through a `@property` with no setter, backed by a private attribute. Assigning raises `AttributeError`. This is still convention, not security, since the private name is reachable; use frozen dataclasses for true immutability.

### Q: What does it mean that `super()` follows the MRO when you add a mixin to `Book`?
`super().__init__()` in the mixin calls the next class in `Book`'s MRO, not a fixed parent, so the mixin must forward `*args, **kwargs` or it cuts the chain. The mixin should come before the base so its initialiser runs first.

## Common Pitfalls

- Making `Library` reach into `Member._borrowed` instead of calling `increment_borrow()`.
- Shadowing a class attribute by assigning to an instance and believing the limit changed globally.
- Defining `__eq__` on `Loan` or `Book` without `__hash__` and then using them in sets.
- Treating a nominal ABC check as if it were duck typing, and rejecting valid third-party classes.
- Using `TypeError` or bare `ValueError` for business-rule failures, which callers cannot distinguish.
- Relying on an in-memory check (`is_available`) for correctness when several workers share the data.
- Letting a mixin swallow `**kwargs`, which silently breaks later classes in the MRO.

## Suggested Extension

Add `Reservation` and a waiting list: when a book is returned, the first reservation becomes a `Loan` automatically. Model the waiting list as a `collections.deque` per ISBN, publish a `BookReturned` event consumed by the reservation handler, and test the sequence with a fake clock so due dates are deterministic.
