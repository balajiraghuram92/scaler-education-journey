# Design Splitwise

Splitwise looks like CRUD until someone asks "who owes whom after forty shared expenses, in as few payments as possible?" That question is a ledger invariant plus a graph problem, and it appears in machine-coding rounds, in fintech interviews and in any FDE project that reconciles money between parties. This lesson is the design half: requirements, the paid/owed model, net balances and the settle-up problem, before the next two lessons write the code.

## Concepts Covered

### Requirements: outside to inside, then the MVP test

Gather requirements from the user's journey (outside) towards the internals (inside), and ask of each one whether it belongs to the MVP. For Splitwise the journey is:

1. A user registers with a name, phone number and password, and can update the profile.
2. Users add **expenses**, optionally inside a **group**, saying who paid what and who owes what.
3. A user sees their total owed amount and the history of expenses they take part in. Only participants see an expense, while every group member sees the group's expenses. Non-members see nothing.
4. Only a group's creator can change its membership.
5. A user can **settle up**: get a list of payments that clears their debts. Settling a group does the same for all members. The system should minimise the number of payments.

Clarify before drawing classes: multiple payers per expense? unequal shares? one currency? Fix the answers (yes, yes, one currency) and write them down.

### The expense model and its invariant

An expense records two things per person: how much they **paid** and how much was **their share** (had to pay). Model each as a list of rows, not as two dictionaries on the expense. Both are the same shape, an amount that belongs to a (user, expense) pair, so they become one table with a type column (the next lesson builds it as `ExpenseUser`).

The invariant that makes the ledger trustworthy: **for every expense, the sum of PAID rows equals the sum of HAD_TO_PAY rows.** Reject anything else at write time. Store money as integer minor units (paise or cents); floats cannot represent most decimals, and a split of 10.00 into three must not create or destroy a paisa.

```python
def split_equally(total_minor: int, users: list[str]) -> dict[str, int]:
    if not users:
        raise ValueError("no participants")
    base, extra = divmod(total_minor, len(users))
    return {u: base + (1 if i < extra else 0) for i, u in enumerate(users)}


shares = split_equally(1000, ["alice", "bob", "carol"])
print(shares, sum(shares.values()))
```

```text
{'alice': 334, 'bob': 333, 'carol': 333} 1000
```

The remainder is handed out one unit at a time, so shares always add back to the total. Pick the recipient rule deliberately (first N users, random, rotating) and document it.

```python
from dataclasses import dataclass
from enum import Enum, auto


class RowType(Enum):
    PAID = auto()
    HAD_TO_PAY = auto()


@dataclass(frozen=True)
class ExpenseUser:
    user: str
    kind: RowType
    amount: int


def validate(rows: list[ExpenseUser]) -> None:
    paid = sum(r.amount for r in rows if r.kind is RowType.PAID)
    owed = sum(r.amount for r in rows if r.kind is RowType.HAD_TO_PAY)
    if paid != owed:
        raise ValueError(f"paid {paid} != owed {owed}")
```

### Net balances

The settle-up input is one number per user: **net balance = total paid minus total owed**, summed over all the expenses in scope. Positive means the user should receive money, negative means they should pay. Because every expense balances, all net balances in the system sum to zero.

```python
from collections import defaultdict


def net_balances(expenses: list[list[ExpenseUser]]) -> dict[str, int]:
    balance: dict[str, int] = defaultdict(int)
    for rows in expenses:
        validate(rows)
        for r in rows:
            balance[r.user] += r.amount if r.kind is RowType.PAID else -r.amount
    return dict(balance)


dinner = [ExpenseUser("A", RowType.PAID, 900)] + [
    ExpenseUser(u, RowType.HAD_TO_PAY, 300) for u in "ABC"
]
cab = [
    ExpenseUser("B", RowType.PAID, 200),
    ExpenseUser("A", RowType.HAD_TO_PAY, 100),
    ExpenseUser("B", RowType.HAD_TO_PAY, 100),
]
print(net_balances([dinner, cab]))
```

```text
{'A': 500, 'B': -200, 'C': -300}
```

Note how A both paid and owed in the same expense: the paid and owed rows for one person do not cancel inside the row set, they cancel in the balance. This also shows why a plain `dict[User, int]` inside `Expense` is awkward: it cannot hold both rows for one user, cannot be queried by user ("all expenses Aman is part of"), and cannot be indexed.

### Settlements are expenses too

When B pays A back, that payment must change future balances. Creating a separate `Transaction` table gives you **two sources of truth** for money moving between people, and every balance query must read both. Model a settlement as a special expense of type `PAYMENT`: payer has a PAID row, receiver has a HAD_TO_PAY row for the same amount. The balance code stays identical.

### The settle-up problem

Given net balances, find payments so that everybody ends at zero. Every payment goes from someone with a negative balance to someone with a positive one. Minimising the **number** of payments is the hard part. It is equivalent to splitting the non-zero balances into the largest possible number of groups that each sum to zero, because a group of k people can be cleared with k-1 payments. That partition problem is NP-hard, so there is no known polynomial algorithm.

Practical options:

| Approach | Transfers | Cost |
|---|---|---|
| Brute force over subsets | Optimal | Exponential in the number of non-zero balances |
| Greedy: largest debtor pays largest creditor | At most n-1, usually good, not always optimal | O(n log n) with heaps |

The greedy step always zeroes at least one person, so it terminates in at most n-1 payments. Here is the exact subset solver for tiny inputs, which also exposes where greedy loses:

```python
def min_transfers(balances: dict[str, int]) -> int:
    vals = [v for v in balances.values() if v]
    m = len(vals)
    if m == 0:
        return 0
    sums = [0] * (1 << m)
    for mask in range(1, 1 << m):
        low = (mask & -mask).bit_length() - 1
        sums[mask] = sums[mask & (mask - 1)] + vals[low]
    best = [0] * (1 << m)          # max zero-sum groups inside each subset
    for mask in range(1, 1 << m):
        best[mask] = max(best[mask ^ (1 << i)] for i in range(m) if mask >> i & 1) + (sums[mask] == 0)
    return m - best[-1]


print(min_transfers({"A": -4, "B": -3, "C": 2, "D": 2, "E": 3}))   # 3
```

For those balances the optimum is 3 payments (A covers C and D; B pays E), while greedy produces 4. The exact solver is O(2^n * n), fine for a group of a dozen and hopeless for hundreds, which is why real apps ship greedy.

> **Interview tip:** Say it plainly: "minimum transfers is NP-hard; I would ship the heap-based greedy, which gives at most n-1 payments in O(n log n), and mention the subset-DP as the exact approach for small groups."

Finally, remember the human angle. A mathematically minimal plan can ask two friends who never met to pay each other. Some products deliberately settle along existing debt edges instead.

## Practical Backend Scenario

A procurement platform lets several departments share cloud costs: each shared GPU reservation is an "expense" paid by one budget and consumed by others. Month-end reconciliation must produce few internal transfers and agree with the ledger. The Splitwise design transfers directly: PAID/HAD_TO_PAY rows, an invariant enforced on write, integer minor units, and settlements recorded as ledger entries.

## Practice Loop

1. Write the requirements list for your own variant and mark each item MVP or later.
2. Implement `split_equally` with a property-style test: shares sum to the total and differ by at most one unit.
3. Implement `validate` and `net_balances`; assert balances sum to zero and that a missing share is rejected.
4. Add a settlement as a `PAYMENT` expense and watch a balance move towards zero.
5. Hand-compute the greedy plan for `[-4, -3, 2, 2, 3]` and compare with `min_transfers`.
6. Sketch the tables: `users`, `user_groups`, group membership, `expenses`, `expense_users`.

## Evidence of Understanding

- You can state the invariant "sum of paid equals sum of owed per expense" and enforce it on write.
- You can compute net balances from rows and explain why all balances sum to zero.
- You can justify a row-per-(expense, user) table over a dictionary inside `Expense`.
- You can explain why settlements are modelled as expenses (one source of truth).
- You can say why minimum-transfer settlement is NP-hard, what greedy guarantees, and give a counterexample.

## Interview Questions to Rehearse

### Q: How do you represent who paid and who owes?

As rows keyed by (expense, user) with an amount and a type, `PAID` or `HAD_TO_PAY`. A dictionary on the expense cannot be queried by user, cannot hold both roles for one person cleanly, and does not map to relational storage. The rows also let balances be computed with one grouped query.

### Q: What invariants would you enforce?

Per expense, paid total equals owed total. Amounts are positive integers in minor units. A settlement has exactly one payer, one receiver and equal amounts. Reject violations when the expense is created, never at settle time.

### Q: How do you minimise the number of settlement payments?

Compute net balances, then pair the largest debtor with the largest creditor repeatedly. Each step clears at least one person, so you get at most n-1 payments in O(n log n). The truly minimal plan is the NP-hard zero-sum partition problem, solvable exactly with subset DP only for small n.

### Q: Why not store settlements in a separate Transaction table?

It creates two sources of truth for money movement, so every report and balance must merge both. A settlement is just money moving between people, so recording it as a `PAYMENT` expense keeps one code path.

## Common Pitfalls

- Letting paid and owed totals diverge, which silently makes balances non-zero-sum.
- Floating-point amounts and rounding each share independently so the sum drifts.
- Computing a user's balance from only one group when the user also has ungrouped expenses.
- Treating minimal transfers as a solved problem, or claiming greedy is optimal.
- Letting non-members read expenses, or letting any member edit group membership.
- Two tables for money movement (expenses and transactions).

## Suggested Extension

Write the query for "expenses visible to user U" that includes group expenses U is not part of, but excludes everyone else's private ones, and add the negative tests.
