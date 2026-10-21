# Code Splitwise 1: Commands, Models and Balances

The Splitwise design becomes code in two moves: a command-driven CLI that keeps `main()` from turning into an `if/elif` ladder, and a relational model where the paid/owed problem is solved by one small table. Both are favourite machine-coding checkpoints, because they reveal whether you spot nouns that deserve a class, choose enums and tables deliberately, and keep every new feature a **new class** instead of an edit to old code.

## Concepts Covered

### Noun spotting: which nouns become classes?

A noun in a requirement is not automatically a class. Ask: do I need to store information about this thing **independently**? If yes, it is a class. If it only describes another object, it is an attribute, and if it is just behaviour or a rule, there is no new class at all.

- "A user registers with name, phone and password": `User` is a class; name, phone and password are attributes.
- "Users participate in expenses": `Expense` is a class (amount, description, who paid, who owes).
- "Users participate in groups": `Group` is a class.
- "A user can view their expense history": a method, not a class.
- "The app shows a list of transactions": a settlement is a special kind of expense, so no `Transaction` class.

### The paid/owed problem and ExpenseUser

`paid_by: dict[User, int]` and `had_to_pay: dict[User, int]` on `Expense` do not map to relational storage. The amount depends on both the user and the expense, which is a many-to-many relationship with a payload. The fix is the same move as `ShowSeat` in BookMyShow: a mapped association class, one row per (expense, user), with a type column saying whether the row is a payment or a share.

Two enums describe the categories. `ExpenseType` is `NORMAL` or `PAYMENT` (a settlement), and `ExpenseUserType` is `PAID` or `HAD_TO_PAY`. They are enums rather than lookup tables because the set changes only with a code release and every user sees the same values. `ExpenseType` lives on `Expense`, `ExpenseUserType` on `ExpenseUser`.

```python
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True      # columns shared by subclasses, no table of its own

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class ExpenseType(enum.Enum):
    NORMAL = enum.auto()
    PAYMENT = enum.auto()


class ExpenseUserType(enum.Enum):
    PAID = enum.auto()
    HAD_TO_PAY = enum.auto()


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class Expense(BaseModel):
    __tablename__ = "expenses"

    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[int] = mapped_column()                 # minor units
    expense_type: Mapped[ExpenseType] = mapped_column(
        SAEnum(ExpenseType, native_enum=False, length=16), default=ExpenseType.NORMAL
    )
    group_id: Mapped[int | None] = mapped_column(ForeignKey("user_groups.id"))
    expense_users: Mapped[list["ExpenseUser"]] = relationship(back_populates="expense")


class ExpenseUser(BaseModel):
    __tablename__ = "expense_users"

    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column()
    expense_user_type: Mapped[ExpenseUserType] = mapped_column(
        SAEnum(ExpenseUserType, native_enum=False, length=16)
    )
    expense: Mapped["Expense"] = relationship(back_populates="expense_users")
    user: Mapped["User"] = relationship()
```

Three traps are visible here. First, `from enum import Enum` followed by `from sqlalchemy import Enum` makes the second name replace the first, and your Python enum stops being one. Import SQLAlchemy's as `SAEnum`. Second, a shared base without `__abstract__ = True` raises an error that the class has no table. Third, table names are plural (`users`, `user_groups`) because `user` and `group` collide with SQL keywords on some databases. `Group.members` is many-to-many through a plain `Table` (built in the next lesson).

Anything the ORM must create tables for has to be **imported** before `create_all`: a model registers on `Base.metadata` only when its module runs. For a throwaway session-scoped app, an in-memory engine is a real database whose contents vanish on exit:

```python
from sqlalchemy import create_engine

import models  # noqa: F401  # imports every model module so they register on Base.metadata
from models.base import Base

engine = create_engine("sqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)
```

### The Command pattern for a CLI

A naive `main()` that parses a line and branches on it violates the single-responsibility and open-closed principles: every new feature edits `main()`. The Command pattern gives each action its own class with two methods: `matches(text)` says whether the line is for me, `execute(text)` does the work. A `CommandExecutor` holds a list of commands and runs the first that matches. Adding `LeaveGroup` means writing one new class and appending it to the list; nothing else changes.

```python
import re
from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def matches(self, user_input: str) -> bool: ...

    @abstractmethod
    def execute(self, user_input: str) -> None: ...


class RegisterUser(Command):
    _RE = re.compile(
        r"register\s+(?P<name>\w+)\s+(?P<phone>\d{10})\s+(?P<password>\S+)", re.IGNORECASE
    )

    def matches(self, user_input: str) -> bool:
        return self._RE.fullmatch(user_input.strip()) is not None

    def execute(self, user_input: str) -> None:
        m = self._RE.fullmatch(user_input.strip())
        assert m is not None
        print(f"registered {m['name']} ({m['phone']})")


class SettleUpUser(Command):
    def matches(self, user_input: str) -> bool:
        words = user_input.split()
        return (
            len(words) == 2
            and words[1].lower() == "settleup"
            and words[0][:1].lower() == "u"
            and words[0][1:].isdigit()
        )

    def execute(self, user_input: str) -> None:
        print(f"settling up user {int(user_input.split()[0][1:])}")


class CommandExecutor:
    def __init__(self, commands: list[Command]) -> None:
        self.commands = commands

    def execute(self, user_input: str) -> None:
        for command in self.commands:
            if command.matches(user_input):
                command.execute(user_input)
                return                      # without this, "Invalid command" prints every time
        print("Invalid command")


executor = CommandExecutor([RegisterUser(), SettleUpUser()])
for line in ["Register asha 9876543210 s3cret", "u12 SettleUp", "u12 SettleUp now", "g1 SettleUp"]:
    executor.execute(line)
```

```text
registered asha (9876543210)
settling up user 12
Invalid command
Invalid command
```

The `return` after `execute` matters: without it the method falls through and prints "Invalid command" after every successful command. Also note `self.commands.matches(...)` (calling the method on the list instead of each element) is an `AttributeError`: iterate and call it on `command`.

Matching strategy deserves thought. `text.startswith("add")` also matches `"address book"`; prefer exact token or regex matching, and write `matches` to be strict, since the first match wins. Because the executor depends only on the `Command` abstraction, you can unit-test each command in isolation and reorder or add commands in `main.py`.

> **Interview tip:** Name the pattern and the principle together: "Command (or Chain-of-Responsibility-style dispatch) keeps `main` closed for modification; a new feature is a new class registered in the composition root."

### Layers: DTOs, controllers, services, repositories

A command parses text and calls a **controller** with a request DTO. The controller maps it to a **service** call, and the service uses **repositories** (a generic base provides `find_by_id`, `save`) over the ORM. DTOs, frozen dataclasses naming exactly what a use case needs, keep ORM objects out of the command layer and give you one place to change when the model changes.

### Computing balances from rows

With rows in `expense_users`, a user's balance is a grouped sum: add `PAID` amounts, subtract `HAD_TO_PAY` amounts. Computing in memory over loaded rows is easy to follow; computing in the database scales better.

```python
from collections import defaultdict


def balances(rows: list[tuple[str, str, int]]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for user, kind, amount in rows:
        out[user] += amount if kind == "PAID" else -amount
    return dict(out)


rows = [("A", "PAID", 900), ("A", "HAD_TO_PAY", 300), ("B", "HAD_TO_PAY", 300), ("C", "HAD_TO_PAY", 300)]
print(balances(rows))
```

```text
{'A': 600, 'B': -300, 'C': -300}
```

The same thing in SQLAlchemy, as one grouped query:

```python
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session


def net_balances(session: Session, expense_ids: list[int]) -> dict[int, int]:
    signed = case(
        (ExpenseUser.expense_user_type == ExpenseUserType.PAID, ExpenseUser.amount),
        else_=-ExpenseUser.amount,
    )
    stmt = (
        select(ExpenseUser.user_id, func.sum(signed))
        .where(ExpenseUser.expense_id.in_(expense_ids))
        .group_by(ExpenseUser.user_id)
    )
    return {user_id: total for user_id, total in session.execute(stmt)}
```

Settlements are stored as `PAYMENT` expenses in the same tables, so these queries need no changes after a payment.

## Practical Backend Scenario

Your team builds an expense-reconciliation assistant for a finance operations client: an LLM chat front end turns "add a 1,200 dinner paid by Asha split among four" into a structured call. The CLI-style command layer is the same idea as tool routing: each tool declares `matches` and `execute`, and unrecognised input falls through to a safe "invalid command" instead of guessing. The row-per-participant model lets the assistant answer "what do I owe?" with one grouped query, with no JSON blobs to parse.

## Practice Loop

1. Run the `Command`/`CommandExecutor` example, then remove `return` and observe the extra "Invalid command" lines.
2. Add a `LeaveGroup` command class and register it in the list, changing no existing class.
3. Change `RegisterUser.matches` to `startswith("register")`, then try an input like `registerx` and see how loose matching misfires.
4. Define the models, import them, create an in-memory SQLite engine and call `create_all` with `echo=True`. Comment out one import and confirm the missing table.
5. Insert one expense with three `ExpenseUser` rows and compute balances in Python and with the grouped query. Compare.
6. Record a settlement as a `PAYMENT` expense and recompute.

## Evidence of Understanding

- You can apply the noun-spotting questions to a requirement and defend each class-versus-attribute decision.
- You can explain why a `dict[User, int]` on `Expense` is the wrong shape and what `ExpenseUser` replaces it with.
- You can justify the two enums over lookup tables and say which model owns each.
- You can explain the Command pattern, name the principle it protects, and add a command without editing the executor.
- You can compute balances from rows in Python and in SQL, and predict what a settlement row changes.

## Interview Questions to Rehearse

### Q: Why not a `Transaction` class for settlements?

A settlement is money moving between people, exactly what an expense models. A separate class creates two sources of truth that every balance query must merge. A `PAYMENT` expense reuses `Expense`, `ExpenseUser` and the balance code.

### Q: Why is `ExpenseUser` a class and not two dictionaries?

The amount depends on the (expense, user) pair, which is a many-to-many relationship with a payload. A table row per pair is queryable by user, indexable and constrained, while a dictionary is opaque to the database and cannot express both roles for one user.

### Q: Enum or lookup table for `ExpenseType`?

An enum, because the values change only with code and are the same for everyone. A lookup table suits values operators edit at runtime or that carry attributes. Remember enums are stored by member name, so renames need a data migration.

### Q: How do you add a new CLI feature without touching `main`?

Implement `Command` (`matches` and `execute`) in a new class and register it in the executor's list in the composition root. The executor depends on the abstraction, so it is closed for modification and open for extension.

### Q: A command executor prints "Invalid command" after every valid command. Why?

The loop does not stop after the first match, so control falls through to the fallback print. Add `return` after `command.execute(...)`.

## Common Pitfalls

- Treating every noun as a class (a `Password` class), or every verb as a method on the wrong class.
- `from sqlalchemy import Enum` shadowing `enum.Enum`.
- Forgetting `__abstract__ = True` on the shared base, or forgetting to import models before `create_all`.
- Loose `startswith` matching in commands, and not returning after the first match.
- Table names that are reserved words (`order`, `group`, `user`).
- Floats for money, and computing balances over a partial row set.

## Suggested Extension

Add `AddExpense`, `CreateGroup` and `MyTotal` commands using a quoted-argument parser (`shlex.split`) so descriptions can contain spaces. Then make `CommandExecutor` return a result object instead of printing, and test every command with no `print` capturing.
