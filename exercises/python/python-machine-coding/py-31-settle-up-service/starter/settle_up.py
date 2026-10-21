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
        """``"<payer> pays <receiver> <amount>"``"""
        raise NotImplementedError("Implement Transaction.__str__")


def net_balances(expenses: Iterable[Expense]) -> dict[str, int]:
    """Paid minus owed per user; zero balances omitted."""
    raise NotImplementedError("Implement net_balances")


class SettleUpStrategy:
    """Make this an abstract base class (``abc.ABC``) with abstract
    ``settle(self, expenses: Sequence[Expense]) -> list[Transaction]``."""


class NaiveSettleUpStrategy(SettleUpStrategy):
    """Sort users by ``(balance, user)`` ascending and walk the list carrying balances.

    For each index ``i`` except the last, with ``amount`` the CARRIED balance of user ``i``:
    ``amount < 0`` -> user ``i`` pays user ``i+1`` ``-amount``; ``amount > 0`` -> user ``i+1`` pays user ``i``
    ``amount``; zero -> nothing. Then add ``amount`` to the carried balance of user ``i+1``. At most n-1 transactions.
    """

    def settle(self, expenses: Sequence[Expense]) -> list[Transaction]:
        raise NotImplementedError("Implement NaiveSettleUpStrategy.settle")


class SettleUpService:
    """Depends on the ``SettleUpStrategy`` abstraction, not a concrete algorithm."""

    def __init__(self, expenses: Sequence[Expense], strategy: SettleUpStrategy) -> None:
        raise NotImplementedError("Implement SettleUpService.__init__")

    def settle_up_user(self, user: str) -> list[Transaction]:
        """Run the strategy on EVERY expense where ``user`` has a row (grouped or not), then return only
        transactions where ``user`` is payer or receiver. Unknown user -> ``[]``."""
        raise NotImplementedError("Implement settle_up_user")

    def settle_up_group(self, group_id: int) -> list[Transaction]:
        """Run the strategy on the expenses with that ``group_id`` and return all transactions."""
        raise NotImplementedError("Implement settle_up_group")


def build_dummy_expense(
    expense_id: int,
    payer: str,
    receiver: str,
    amount: int,
    group_id: int | None = None,
) -> Expense:
    """Payer has a PAID row and receiver a HAD_TO_PAY row of ``amount``.

    ``amount`` must be a positive int and the users must differ, otherwise ValueError.
    """
    raise NotImplementedError("Implement build_dummy_expense")
