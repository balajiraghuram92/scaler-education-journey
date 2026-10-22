from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto


class LedgerError(ValueError):
    """An expense or row breaks a ledger rule."""


class RowType(Enum):
    PAID = auto()
    HAD_TO_PAY = auto()


class ExpenseKind(Enum):
    NORMAL = auto()
    PAYMENT = auto()


@dataclass(frozen=True)
class ExpenseUser:
    """One row: ``user`` PAID or HAD_TO_PAY ``amount`` minor units.

    ``amount`` must be a positive int (booleans and floats are rejected) -> LedgerError.
    """

    user: str
    kind: RowType
    amount: int


@dataclass(frozen=True)
class Expense:
    """A validated expense (validate in ``__post_init__`` so an invalid one can never exist).

    Rules, all raising LedgerError: at least one PAID and one HAD_TO_PAY row; total paid == total owed;
    a PAYMENT has exactly one row of each type and the two users differ.
    """

    expense_id: int
    rows: tuple[ExpenseUser, ...]
    kind: ExpenseKind = ExpenseKind.NORMAL


def net_balances(expenses: Iterable[Expense]) -> dict[str, int]:
    """Per user: total paid minus total owed. Exactly-zero balances are omitted."""
    raise NotImplementedError("Implement net_balances")


def record_settlement(expense_id: int, payer: str, receiver: str, amount: int) -> Expense:
    """A PAYMENT expense: ``payer`` has a PAID row, ``receiver`` a HAD_TO_PAY row."""
    raise NotImplementedError("Implement record_settlement")


def expenses_for_user(expenses: Iterable[Expense], user: str) -> list[Expense]:
    """Expenses where ``user`` has at least one row, sorted by ``expense_id``."""
    raise NotImplementedError("Implement expenses_for_user")
