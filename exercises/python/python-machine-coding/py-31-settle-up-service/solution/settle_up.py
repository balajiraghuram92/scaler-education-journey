from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable, Sequence
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


@dataclass(frozen=True)
class Expense:
    expense_id: int
    rows: tuple[ExpenseUser, ...]
    group_id: int | None = None


@dataclass(frozen=True)
class Transaction:
    payer: str
    receiver: str
    amount: int

    def __str__(self) -> str:
        return f"{self.payer} pays {self.receiver} {self.amount}"


def net_balances(expenses: Iterable[Expense]) -> dict[str, int]:
    balance: defaultdict[str, int] = defaultdict(int)
    for expense in expenses:
        for row in expense.rows:
            balance[row.user] += row.amount if row.kind is RowType.PAID else -row.amount
    return {user: amount for user, amount in balance.items() if amount != 0}


class SettleUpStrategy(ABC):
    @abstractmethod
    def settle(self, expenses: Sequence[Expense]) -> list[Transaction]: ...


class NaiveSettleUpStrategy(SettleUpStrategy):
    def settle(self, expenses: Sequence[Expense]) -> list[Transaction]:
        balances = net_balances(expenses)
        order = sorted(balances, key=lambda user: (balances[user], user))
        carry = [balances[user] for user in order]
        transactions: list[Transaction] = []
        for i in range(len(order) - 1):
            amount = carry[i]
            if amount < 0:
                transactions.append(Transaction(order[i], order[i + 1], -amount))
            elif amount > 0:
                transactions.append(Transaction(order[i + 1], order[i], amount))
            carry[i + 1] += amount
        return transactions


class SettleUpService:
    def __init__(self, expenses: Sequence[Expense], strategy: SettleUpStrategy) -> None:
        self.expenses = expenses
        self.strategy = strategy

    def settle_up_user(self, user: str) -> list[Transaction]:
        involved = [e for e in self.expenses if any(row.user == user for row in e.rows)]
        transactions = self.strategy.settle(involved)
        return [t for t in transactions if user in (t.payer, t.receiver)]

    def settle_up_group(self, group_id: int) -> list[Transaction]:
        group_expenses = [e for e in self.expenses if e.group_id == group_id]
        return self.strategy.settle(group_expenses)


def build_dummy_expense(
    expense_id: int,
    payer: str,
    receiver: str,
    amount: int,
    group_id: int | None = None,
) -> Expense:
    if type(amount) is not int or amount <= 0:
        raise ValueError("amount must be a positive integer")
    if payer == receiver:
        raise ValueError("payer and receiver must differ")
    return Expense(
        expense_id,
        (
            ExpenseUser(payer, RowType.PAID, amount),
            ExpenseUser(receiver, RowType.HAD_TO_PAY, amount),
        ),
        group_id,
    )
