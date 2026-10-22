from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto


class LedgerError(ValueError):
    pass


class RowType(Enum):
    PAID = auto()
    HAD_TO_PAY = auto()


class ExpenseKind(Enum):
    NORMAL = auto()
    PAYMENT = auto()


@dataclass(frozen=True)
class ExpenseUser:
    user: str
    kind: RowType
    amount: int

    def __post_init__(self) -> None:
        if type(self.amount) is not int or self.amount <= 0:
            raise LedgerError(f"amount must be a positive integer, got {self.amount!r}")


@dataclass(frozen=True)
class Expense:
    expense_id: int
    rows: tuple[ExpenseUser, ...]
    kind: ExpenseKind = ExpenseKind.NORMAL

    def __post_init__(self) -> None:
        paid_rows = [r for r in self.rows if r.kind is RowType.PAID]
        owed_rows = [r for r in self.rows if r.kind is RowType.HAD_TO_PAY]
        if not paid_rows or not owed_rows:
            raise LedgerError("an expense needs at least one PAID and one HAD_TO_PAY row")
        paid = sum(r.amount for r in paid_rows)
        owed = sum(r.amount for r in owed_rows)
        if paid != owed:
            raise LedgerError(f"paid {paid} != owed {owed}")
        if self.kind is ExpenseKind.PAYMENT:
            if len(paid_rows) != 1 or len(owed_rows) != 1:
                raise LedgerError("a PAYMENT has exactly one payer and one receiver")
            if paid_rows[0].user == owed_rows[0].user:
                raise LedgerError("payer and receiver must differ")


def net_balances(expenses: Iterable[Expense]) -> dict[str, int]:
    balance: defaultdict[str, int] = defaultdict(int)
    for expense in expenses:
        for row in expense.rows:
            balance[row.user] += row.amount if row.kind is RowType.PAID else -row.amount
    return {user: amount for user, amount in balance.items() if amount != 0}


def record_settlement(expense_id: int, payer: str, receiver: str, amount: int) -> Expense:
    return Expense(
        expense_id,
        (
            ExpenseUser(payer, RowType.PAID, amount),
            ExpenseUser(receiver, RowType.HAD_TO_PAY, amount),
        ),
        ExpenseKind.PAYMENT,
    )


def expenses_for_user(expenses: Iterable[Expense], user: str) -> list[Expense]:
    involved = [e for e in expenses if any(r.user == user for r in e.rows)]
    return sorted(involved, key=lambda e: e.expense_id)
