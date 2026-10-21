from __future__ import annotations

import itertools
import threading
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass


class BudgetExceededError(Exception):
    def __init__(self, tenant: str, limit: str) -> None:
        super().__init__(f"{tenant} would exceed the {limit} limit")
        self.tenant, self.limit = tenant, limit


class UnknownCallError(Exception):
    """refund() was called for a call id that does not exist or was already refunded."""


@dataclass(frozen=True)
class _Call:
    tenant: str
    usage: tuple[tuple[str, int], ...]


class BudgetGuard:
    """Per-tenant running counters: charge and refund are O(number of limits), never O(history)."""

    def __init__(self, caps: Mapping[str, int]) -> None:
        self._caps = dict(caps)
        self._used: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._calls: dict[int, _Call] = {}
        self._ids = itertools.count(1)
        self._lock = threading.Lock()

    def charge(self, tenant: str, usage: Mapping[str, int]) -> int:
        for name, amount in usage.items():
            if name not in self._caps:
                raise ValueError(f"unknown limit: {name}")
            if amount < 0:
                raise ValueError("usage must be non-negative")
        with self._lock:                         # check-then-act must be one atomic step
            used = self._used[tenant]
            for name, amount in usage.items():   # validate everything first ...
                if used[name] + amount > self._caps[name]:
                    raise BudgetExceededError(tenant, name)
            for name, amount in usage.items():   # ... then mutate
                used[name] += amount
            call_id = next(self._ids)
            self._calls[call_id] = _Call(tenant, tuple(sorted(usage.items())))
            return call_id

    def refund(self, call_id: int) -> None:
        with self._lock:
            call = self._calls.pop(call_id, None)
            if call is None:
                raise UnknownCallError(call_id)
            for name, amount in call.usage:
                self._used[call.tenant][name] -= amount

    def used(self, tenant: str, limit: str) -> int:
        with self._lock:
            return self._used[tenant][limit] if tenant in self._used else 0


class RescanGuard:
    """The slow, obviously correct oracle: recompute usage from the full history."""

    def __init__(self, caps: Mapping[str, int]) -> None:
        self._caps = dict(caps)
        self._calls: dict[int, tuple[str, dict[str, int]]] = {}
        self._ids = itertools.count(1)

    def used(self, tenant: str, limit: str) -> int:
        return sum(u.get(limit, 0) for t, u in self._calls.values() if t == tenant)

    def charge(self, tenant: str, usage: Mapping[str, int]) -> int:
        for name, amount in usage.items():
            if self.used(tenant, name) + amount > self._caps[name]:
                raise BudgetExceededError(tenant, name)
        call_id = next(self._ids)
        self._calls[call_id] = (tenant, dict(usage))
        return call_id

    def refund(self, call_id: int) -> None:
        if self._calls.pop(call_id, None) is None:
            raise UnknownCallError(call_id)
