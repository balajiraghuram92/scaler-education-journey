from __future__ import annotations
import itertools
import threading
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

class BudgetExceededError(Exception):

    def __init__(self, tenant: str, limit: str) -> None:
        super().__init__(f'{tenant} would exceed the {limit} limit')
        self.tenant, self.limit = (tenant, limit)

class UnknownCallError(Exception):
    """refund() was called for a call id that does not exist or was already refunded."""

@dataclass(frozen=True)
class _Call:
    tenant: str
    usage: tuple[tuple[str, int], ...]

class BudgetGuard:
    """Per-tenant running counters: charge and refund are O(number of limits), never O(history)."""

    def __init__(self, caps: Mapping[str, int]) -> None:
        """Keep the caps, per-tenant per-limit counters, the live calls by id, an id counter and a lock."""
        raise NotImplementedError('TODO: implement __init__')

    def charge(self, tenant: str, usage: Mapping[str, int]) -> int:
        """Raise ValueError for an unknown limit or a negative amount. Then, under the lock, check every limit and raise BudgetExceededError(tenant, limit) if any would exceed its cap; only after all checks pass update the counters, record the call and return its id."""
        raise NotImplementedError('TODO: implement charge')

    def refund(self, call_id: int) -> None:
        """Under the lock, remove the call and subtract exactly what it charged. Unknown or already refunded ids raise UnknownCallError."""
        raise NotImplementedError('TODO: implement refund')

    def used(self, tenant: str, limit: str) -> int:
        """Current usage of the limit for the tenant (0 for an unknown tenant)."""
        raise NotImplementedError('TODO: implement used')

class RescanGuard:
    """The slow, obviously correct oracle: recompute usage from the full history."""

    def __init__(self, caps: Mapping[str, int]) -> None:
        """Keep the caps and every live call (no counters)."""
        raise NotImplementedError('TODO: implement __init__')

    def used(self, tenant: str, limit: str) -> int:
        """Recompute usage by summing over all live calls of the tenant."""
        raise NotImplementedError('TODO: implement used')

    def charge(self, tenant: str, usage: Mapping[str, int]) -> int:
        """Same contract as BudgetGuard.charge, built on used()."""
        raise NotImplementedError('TODO: implement charge')

    def refund(self, call_id: int) -> None:
        """Same contract as BudgetGuard.refund."""
        raise NotImplementedError('TODO: implement refund')
