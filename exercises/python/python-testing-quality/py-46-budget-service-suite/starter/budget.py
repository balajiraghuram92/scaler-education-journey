from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class BudgetExceeded(Exception):
    """Raised when a charge would push a tenant over its limit.

    Attributes (all required): ``tenant``, ``used``, ``requested``, ``limit``.
    The message must be ``"<tenant>: <used>+<requested> exceeds limit <limit>"``.
    """

    def __init__(self, tenant: str, used: int, requested: int, limit: int) -> None:
        raise NotImplementedError("Implement BudgetExceeded.__init__")


class UsageRepo(Protocol):
    def get(self, tenant: str) -> int: ...
    def add(self, tenant: str, tokens: int) -> int: ...


@dataclass
class InMemoryUsageRepo:
    """Fake repo. Unknown tenants have usage 0; ``add`` returns the new running total."""

    rows: dict[str, int] = field(default_factory=dict)

    def get(self, tenant: str) -> int:
        raise NotImplementedError("Implement InMemoryUsageRepo.get")

    def add(self, tenant: str, tokens: int) -> int:
        raise NotImplementedError("Implement InMemoryUsageRepo.add")


@dataclass
class BudgetService:
    repo: UsageRepo
    limit: int

    def charge(self, tenant: str, tokens: int) -> int:
        """Record usage and return the new total.

        - ``tokens <= 0`` -> ``ValueError("tokens must be positive")``
        - ``used + tokens > limit`` -> ``BudgetExceeded`` (and nothing is stored)
        - charging exactly up to the limit is allowed
        """
        raise NotImplementedError("Implement BudgetService.charge")

    def remaining(self, tenant: str) -> int:
        """Return ``limit - current usage`` for the tenant."""
        raise NotImplementedError("Implement BudgetService.remaining")
