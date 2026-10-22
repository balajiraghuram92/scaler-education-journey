from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Literal, Protocol, Self

Status = Literal["pending", "captured", "failed"]


class DuplicateKey(Exception):
    pass


class GatewayError(Exception):
    pass


class PaymentInFlight(Exception):
    pass


@dataclass(frozen=True)
class Payment:
    key: str
    tenant: str
    amount_cents: int
    status: Status = "pending"
    provider_ref: str | None = None


class PaymentRepository(Protocol):
    async def get(self, key: str) -> Payment | None: ...
    async def add(self, payment: Payment) -> None: ...  # raises DuplicateKey
    async def save(self, payment: Payment) -> None: ...


class Gateway(Protocol):
    async def capture(self, tenant: str, amount_cents: int) -> str: ...  # raises GatewayError


class UnitOfWork(Protocol):
    payments: PaymentRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None: ...
    async def commit(self) -> None: ...


class PaymentService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork], gateway: Gateway) -> None:
        """``uow_factory()`` returns a *new* unit of work every time it is called."""
        raise NotImplementedError("Implement __init__")

    async def charge(self, key: str, tenant: str, amount_cents: int) -> Payment:
        """Charge exactly once per ``key``.

        - ``amount_cents <= 0`` raises ``ValueError`` before touching any port
        - step 1 (one unit of work): ``add`` a ``pending`` payment and ``commit()``. If ``add`` raises
          ``DuplicateKey``, load the existing payment: if it is ``pending`` raise ``PaymentInFlight``,
          otherwise return it unchanged (idempotent replay)
        - step 2 (no transaction open): ``gateway.capture(tenant, amount_cents)``
        - step 3 (a new unit of work): ``save`` the final payment (``captured`` with ``provider_ref``,
          or ``failed`` on ``GatewayError``) and ``commit()``; after recording a failure re-raise
          ``GatewayError``
        - a failed payment is terminal for its key: a retry returns it without calling the gateway
        """
        raise NotImplementedError("Implement charge")
