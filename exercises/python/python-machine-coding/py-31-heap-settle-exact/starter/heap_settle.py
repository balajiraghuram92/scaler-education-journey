from collections.abc import Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Transfer:
    payer: str
    receiver: str
    amount: int


def settle_heap(balances: Mapping[str, int]) -> list[Transfer]:
    """Greedy settle-up with two ``heapq`` heaps (creditors and debtors) keyed by ``(-amount, user)``.

    - positive balance = should receive; zero balances are ignored
    - balances must sum to zero (ValueError); non-int balances raise TypeError
    - each step pops the largest creditor and largest debtor (ties: alphabetically smallest user),
      transfers ``min(credit, debt)`` and pushes back whoever has a remainder
    - the result must not depend on the insertion order of ``balances``
    """
    raise NotImplementedError("Implement settle_heap")


def min_transfers_exact(balances: Mapping[str, int]) -> int:
    """True minimum number of transfers: ``m - G`` where ``m`` is the number of non-zero balances and ``G`` the
    maximum number of disjoint zero-sum groups (bitmask DP over subsets). ValueError if ``m > 16``."""
    raise NotImplementedError("Implement min_transfers_exact")


def apply_transfers(balances: Mapping[str, int], transfers: Iterable[Transfer]) -> dict[str, int]:
    """Balances after applying the transfers (payer ``+amount``, receiver ``-amount``), omitting zeros."""
    raise NotImplementedError("Implement apply_transfers")
