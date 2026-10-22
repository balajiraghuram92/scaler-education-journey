from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

class PaymentStatus(Enum):
    SUCCESS = 'success'
    FAILED = 'failed'

class SpotStatus(Enum):
    AVAILABLE = 'available'
    OCCUPIED = 'occupied'

@dataclass(eq=False)
class Spot:
    number: int
    status: SpotStatus = SpotStatus.OCCUPIED

@dataclass(frozen=True)
class Payment:
    amount: float
    mode: str
    status: PaymentStatus

@dataclass(eq=False)
class Bill:
    amount: float
    spot: Spot
    payments: list[Payment]

    @property
    def total_paid(self) -> float:
        """Sum of the amounts of SUCCESS payments only."""
        raise NotImplementedError('TODO: implement total_paid')

    @property
    def is_paid(self) -> bool:
        """True when total_paid >= amount."""
        raise NotImplementedError('TODO: implement is_paid')

class OverpaymentError(Exception):
    pass

class PaymentService:
    """Plain values in, a model out. The gateway is injected: it returns True when the charge went through."""

    def __init__(self, gateway: Callable[[float, str], bool]) -> None:
        """Keep the injected gateway (amount, mode) -> bool."""
        raise NotImplementedError('TODO: implement __init__')

    def make_payment(self, bill: Bill, amount: float, mode: str) -> Payment:
        """Raise OverpaymentError when amount exceeds what is outstanding, before calling the gateway. Otherwise call the gateway, append a Payment (SUCCESS or FAILED) to bill.payments and return it. When the bill is now paid, set bill.spot.status to AVAILABLE."""
        raise NotImplementedError('TODO: implement make_payment')
