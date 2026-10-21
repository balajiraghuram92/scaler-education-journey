from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class PaymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"


class SpotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"


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
        """Only successful payments count: a failed attempt is kept for the audit trail but adds nothing."""
        return sum(p.amount for p in self.payments if p.status is PaymentStatus.SUCCESS)

    @property
    def is_paid(self) -> bool:
        return self.total_paid >= self.amount


class OverpaymentError(Exception):
    pass


class PaymentService:
    """Plain values in, a model out. The gateway is injected: it returns True when the charge went through."""

    def __init__(self, gateway: Callable[[float, str], bool]) -> None:
        self._gateway = gateway

    def make_payment(self, bill: Bill, amount: float, mode: str) -> Payment:
        if amount > bill.amount - bill.total_paid:
            raise OverpaymentError(f"only {bill.amount - bill.total_paid} is outstanding")
        ok = self._gateway(amount, mode)
        payment = Payment(amount, mode, PaymentStatus.SUCCESS if ok else PaymentStatus.FAILED)
        bill.payments.append(payment)
        if bill.is_paid:
            bill.spot.status = SpotStatus.AVAILABLE      # free the spot only when the bill is settled
        return payment
