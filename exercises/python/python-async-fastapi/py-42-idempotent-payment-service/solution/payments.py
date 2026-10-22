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
        self._uow_factory = uow_factory
        self._gateway = gateway

    async def charge(self, key: str, tenant: str, amount_cents: int) -> Payment:
        if amount_cents <= 0:
            raise ValueError("amount_cents must be positive")
        pending = Payment(key, tenant, amount_cents)
        async with self._uow_factory() as uow:
            try:
                await uow.payments.add(pending)
                await uow.commit()
            except DuplicateKey:
                existing = await uow.payments.get(key)
                if existing is None:  # defensive: row vanished between add and get
                    raise PaymentInFlight(key) from None
                if existing.status == "pending":
                    raise PaymentInFlight(key) from None
                return existing
        try:
            ref = await self._gateway.capture(tenant, amount_cents)
        except GatewayError:
            await self._finish(replace(pending, status="failed"))
            raise
        return await self._finish(replace(pending, status="captured", provider_ref=ref))

    async def _finish(self, payment: Payment) -> Payment:
        async with self._uow_factory() as uow:
            await uow.payments.save(payment)
            await uow.commit()
        return payment
