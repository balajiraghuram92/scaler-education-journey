from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class BudgetExceeded(Exception):
    def __init__(self, tenant: str, used: int, requested: int, limit: int) -> None:
        super().__init__(f"{tenant}: {used}+{requested} exceeds limit {limit}")
        self.tenant = tenant
        self.used = used
        self.requested = requested
        self.limit = limit


class UsageRepo(Protocol):
    def get(self, tenant: str) -> int: ...
    def add(self, tenant: str, tokens: int) -> int: ...


@dataclass
class InMemoryUsageRepo:
    rows: dict[str, int] = field(default_factory=dict)

    def get(self, tenant: str) -> int:
        return self.rows.get(tenant, 0)

    def add(self, tenant: str, tokens: int) -> int:
        self.rows[tenant] = self.get(tenant) + tokens
        return self.rows[tenant]


@dataclass
class BudgetService:
    repo: UsageRepo
    limit: int

    def charge(self, tenant: str, tokens: int) -> int:
        """Record usage and return the new total; reject without side effects."""
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        used = self.repo.get(tenant)
        if used + tokens > self.limit:
            raise BudgetExceeded(tenant, used, tokens, self.limit)
        return self.repo.add(tenant, tokens)

    def remaining(self, tenant: str) -> int:
        return self.limit - self.repo.get(tenant)
