# Code Splitwise 2: Settle-Up Strategies

This lesson finishes the Splitwise machine-coding problem: many-to-many group membership, settlements stored as expenses, and two interchangeable settle-up algorithms behind one interface. The payoff in an interview is the last step: swapping a naive algorithm for a heap-based one by changing exactly one line in `main.py`, which is the Strategy pattern and dependency inversion doing their jobs, and then being able to state the complexity and where the greedy approach stops being optimal.

## Concepts Covered

### Many-to-many membership with `secondary`

Riya is in the "Goa Trip" group and in "Roommates", and each group has many members. That is many-to-many, so no single foreign key can express it. A plain association `Table` (two foreign keys forming a composite primary key) joins them, and both sides declare `relationship(secondary=...)` with `back_populates` so the in-memory collections stay in sync. When the link has no data of its own, a `Table` is enough; when it needs attributes, promote it to a class, as `ExpenseUser` was.

```python
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", ForeignKey("user_groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class Group(BaseModel):
    __tablename__ = "user_groups"

    name: Mapped[str] = mapped_column(String(100))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    members: Mapped[list["User"]] = relationship(
        secondary=group_members, back_populates="groups"
    )
    expenses: Mapped[list["Expense"]] = relationship()


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100))
    groups: Mapped[list["Group"]] = relationship(
        secondary=group_members, back_populates="members"
    )
```

Two details recur in reviews. `created_at` defaults must be a callable (`default=utc_now`), because `default=datetime.now(timezone.utc)` runs once at import, so every row gets the same stale time. And `back_populates` creates no extra table and no foreign key; it only keeps `expense.expense_users` and `expense_user.expense` consistent in memory, so appending to one side shows up on the other before any flush. The `Expense` model carries `expense_type` (an `ExpenseType` enum: `NORMAL` or `PAYMENT`), while `ExpenseUser` carries `expense_user_type`.

> **Pitfall:** enums are stored by member **name**. If you rename `PAYMENT` to `SETTLEMENT`, old rows still hold the text `PAYMENT`, and loading one raises a `LookupError` because no member has that name. Rename with a data migration, never just in code.

### A settlement is an expense

B pays A 300. Record it as a dummy `Expense` of type `PAYMENT`: the payer gets a `PAID` row and the receiver a `HAD_TO_PAY` row, for the same amount. The invariant "total paid equals total owed" must still hold. Marking both rows `PAID` is a classic bug: total paid is 600 and total owed 0, and every balance after it is wrong.

```python
def build_dummy_expense(expense_id: int, payer: int, receiver: int, amount: int) -> Expense:
    return Expense(
        expense_id,
        (
            ExpenseUser(payer, RowType.PAID, amount),
            ExpenseUser(receiver, RowType.HAD_TO_PAY, amount),
        ),
    )
```

Because it reuses `Expense` and `ExpenseUser`, balance code needs no knowledge that settlements exist.

### The Strategy pattern for settle-up

Settle-up has several valid algorithms. Put the contract in an abstract class, and let the service depend on it. The service computes nothing about balances itself; the strategy receives expenses and returns `Transaction`s.

```python
import heapq
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto


class RowType(Enum):
    PAID = auto()
    HAD_TO_PAY = auto()


@dataclass(frozen=True)
class ExpenseUser:
    user: int
    kind: RowType
    amount: int


@dataclass(frozen=True)
class Expense:
    expense_id: int
    rows: tuple[ExpenseUser, ...]


@dataclass(frozen=True)
class Transaction:
    payer: int
    receiver: int
    amount: int

    def __str__(self) -> str:
        return f"{self.payer} pays {self.receiver} {self.amount}"


def net_balances(expenses: Sequence[Expense]) -> dict[int, int]:
    balance: dict[int, int] = defaultdict(int)
    for expense in expenses:
        for row in expense.rows:
            balance[row.user] += row.amount if row.kind is RowType.PAID else -row.amount
    return {u: v for u, v in balance.items() if v}


class SettleUpStrategy(ABC):
    @abstractmethod
    def settle(self, expenses: Sequence[Expense]) -> list[Transaction]: ...
```

**Naive strategy.** Sort users from the lowest balance to the highest. Walk the sorted list: each person settles fully with the **next** person, and the remaining amount is carried to that next person. It is simple and yields at most n-1 transactions in O(n log n) (the sort dominates), but money may flow through intermediaries: with balances A = -300, B = -200, C = +500 it produces "A pays B 300, then B pays C 500", a transfer between two debtors.

```python
class NaiveSettleUpStrategy(SettleUpStrategy):
    def settle(self, expenses: Sequence[Expense]) -> list[Transaction]:
        balances = net_balances(expenses)
        order = sorted(balances, key=lambda u: (balances[u], u))
        carry = [balances[u] for u in order]
        txns: list[Transaction] = []
        for i in range(len(order) - 1):
            amount = carry[i]
            if amount < 0:
                txns.append(Transaction(order[i], order[i + 1], -amount))
            elif amount > 0:
                txns.append(Transaction(order[i + 1], order[i], amount))
            carry[i + 1] += amount
        return txns
```

**Heap strategy.** Keep two max-heaps: debtors and creditors. Repeatedly pop the largest of each, pay `min(debt, credit)`, and push back whoever still has a remainder. Each step settles at least one person, so there are at most n-1 transactions, and every transaction goes directly from someone who owes to someone who is owed. Python's `heapq` is a **min**-heap, so store negated amounts. Each of the up to n iterations does O(log n) heap work: **O(n log n)** time, O(n) space.

```python
class HeapSettleUpStrategy(SettleUpStrategy):
    def settle(self, expenses: Sequence[Expense]) -> list[Transaction]:
        balances = net_balances(expenses)
        creditors = [(-v, u) for u, v in balances.items() if v > 0]
        debtors = [(v, u) for u, v in balances.items() if v < 0]
        heapq.heapify(creditors)
        heapq.heapify(debtors)
        txns: list[Transaction] = []
        while creditors and debtors:
            neg_credit, creditor = heapq.heappop(creditors)
            neg_debt, debtor = heapq.heappop(debtors)
            credit, debt = -neg_credit, -neg_debt
            pay = min(credit, debt)
            txns.append(Transaction(debtor, creditor, pay))
            if credit > pay:
                heapq.heappush(creditors, (-(credit - pay), creditor))
            if debt > pay:
                heapq.heappush(debtors, (-(debt - pay), debtor))
        return txns
```

Tuples compare element by element, so equal amounts fall back to the user id: keep ids comparable. Run on the dinner and cab expenses from the earlier lessons (balances 1: +500, 2: -200, 3: -300):

```text
Naive: ['3 pays 2 300', '2 pays 1 500']
Heap:  ['3 pays 1 300', '2 pays 1 200']
```

Same number of transactions here, but the heap plan never routes money through a debtor. Neither is guaranteed minimal: minimising transactions is the NP-hard zero-sum partition problem. For balances `[-4, -3, +2, +2, +3]` both strategies use 4 payments while 3 suffice.

### The service filters, the controller translates

`settle_up_user(user)` must find every expense the user takes part in. Aman may be in five groups **and** have ungrouped one-to-one expenses, so start from his `ExpenseUser` rows, not from groups: find those rows, then take each row's expense. Run the strategy on that set and keep only transactions where the user is payer or receiver. A transaction between two other people does not affect him.

```python
class SettleUpService:
    def __init__(self, expenses: Sequence[Expense], strategy: SettleUpStrategy) -> None:
        self.expenses = expenses
        self.strategy = strategy

    def settle_up_user(self, user_id: int) -> list[Transaction]:
        involved = [e for e in self.expenses if any(r.user == user_id for r in e.rows)]
        return [t for t in self.strategy.settle(involved) if user_id in (t.payer, t.receiver)]
```

In the real project the first line is a repository query: select `ExpenseUser` rows by `user_id`, then load the expenses. Python does **not** enforce annotations at runtime: a controller typed `request: SettleUpUserResponseDto` but passed a request DTO runs fine, because only a static checker (pyright, mypy) flags it. Run one in CI.

### Wiring at one point

Only `main.py`, the composition root, names concrete classes. Swapping algorithms is a one-line change there, because the service, controller and command depend on the abstraction:

```python
strategy = HeapSettleUpStrategy()                 # was NaiveSettleUpStrategy()
service = SettleUpService(expenses, strategy)
controller = SettleUpController(service)
executor = CommandExecutor([RegisterUser(...), SettleUpUser(controller)])
```

`SettleUpUser.matches` accepts exactly two words, the second `settleup` ignoring case, the first starting with `u` (any case) followed only by digits. So `u12 SettleUp` and `U3 settleup` match, while `g1 SettleUp` and `u1 SettleUp now` do not. And in the executor, iterate and call `command.matches(...)`: writing `self.commands.matches(...)` calls a method on a list and raises `AttributeError`.

## Practical Backend Scenario

You are an FDE for a client that runs shared GPU budgets across teams, with a nightly job that proposes internal transfers. Finance asks for "fewer transfers" after seeing the naive output route money through intermediate teams. Because settle-up sits behind `SettleUpStrategy`, you ship `HeapSettleUpStrategy` behind a flag in the composition root, compare outputs on a month of real ledger data (each plan must zero every balance and never exceed n-1 transfers), and roll back by flipping the flag. You also note honestly that the plan is near-minimal, not provably minimal.

## Practice Loop

1. Implement `net_balances`, both strategies and `SettleUpService`. Test that applying each plan zeroes every balance.
2. Property-test with random balanced expenses: transfers never exceed the number of non-zero balances minus one, and no transfer is for zero or a negative amount.
3. Run both strategies on `[-4, -3, 2, 2, 3]`, then write the 3-payment plan by hand.
4. Build `build_dummy_expense`, add it to the ledger, and re-run settle-up to see balances move.
5. Create `Group` and `User` with `secondary`, append a user to `group.members`, and print `user.groups` before any flush.
6. Swap strategies in `main.py` only, and confirm no other file changes.

## Evidence of Understanding

- You can model a many-to-many relationship with `secondary` and `back_populates`, and say when to promote the join table to a class.
- You can state the settlement rows (`PAID` for the payer, `HAD_TO_PAY` for the receiver) and the rule they must keep.
- You can describe naive and heap settle-up, give each one's complexity and transaction bound, and explain `heapq`'s negation trick.
- You can explain why settle-up for a user starts from `ExpenseUser` rows and filters transactions.
- You can show that greedy is not always minimal and why that is acceptable.
- You can explain what the composition root is and why a strategy swap is one line.

## Interview Questions to Rehearse

### Q: Walk me through your settle-up algorithm and its complexity.

Compute each user's net balance in one pass over the rows. Put positive balances in a max-heap of creditors and negative ones in a max-heap of debtors (negated for `heapq`). Pop the largest of each, transfer the smaller magnitude, and push back the remainder. Each iteration settles at least one person, so there are at most n-1 transfers, and each does O(log n) heap work: O(n log n) overall.

### Q: Is that the minimum number of transactions?

Not always. Minimum transfers is equivalent to splitting the non-zero balances into the maximum number of zero-sum groups, which is NP-hard. Greedy bounds the count at n-1 and is usually close. For small groups an exact subset DP works.

### Q: Why is a settlement stored as an expense?

It is money moving between people, so it reuses `Expense` and `ExpenseUser` and keeps a single source of truth for balances. The payer has a `PAID` row and the receiver a `HAD_TO_PAY` row of equal amount, which preserves the paid-equals-owed rule.

### Q: How do you find every expense for a user?

Query `ExpenseUser` rows for that user and take each row's expense, which covers all groups and ungrouped expenses. Starting from groups would miss one-to-one expenses.

### Q: How do you make the algorithm swappable?

Define an abstract `SettleUpStrategy` and inject a concrete one into `SettleUpService` from `main.py`. The service and controller depend on the abstraction, so replacing `NaiveSettleUpStrategy()` with `HeapSettleUpStrategy()` is a one-line change and each strategy is unit-testable alone.

### Q: A teammate's type hints are wrong but the code runs. Is that a problem?

Python ignores annotations at runtime, so it runs, but the mistake hides real contract drift. Run pyright or mypy in CI so a wrong hint fails the build.

## Common Pitfalls

- Marking both rows of a settlement `PAID`, which breaks paid-equals-owed.
- Settling up from a single group and missing ungrouped expenses.
- Returning transactions that do not involve the requested user.
- Using `heapq` as a max-heap without negating, or heap tuples with non-comparable tie-breakers.
- Renaming enum members without migrating stored names.
- `default=datetime.now(...)` instead of a callable.
- `self.commands.matches(...)` instead of calling `matches` on each command.
- Claiming greedy settle-up is optimal.

## Suggested Extension

Implement the exact subset-DP strategy for groups up to 12 people, and make the service choose it automatically when the number of non-zero balances is small, falling back to the heap otherwise. Add a test that compares both on random balances and asserts the exact plan never uses more transfers than the heap plan.
