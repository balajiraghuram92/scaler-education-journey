import heapq
from collections.abc import Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Transfer:
    payer: str
    receiver: str
    amount: int


def _clean(balances: Mapping[str, int]) -> dict[str, int]:
    for user, value in balances.items():
        if type(value) is not int:
            raise TypeError(f"balance of {user!r} must be an int")
    if sum(balances.values()) != 0:
        raise ValueError("balances must sum to zero")
    return {user: value for user, value in balances.items() if value != 0}


def settle_heap(balances: Mapping[str, int]) -> list[Transfer]:
    cleaned = _clean(balances)
    creditors = [(-v, u) for u, v in cleaned.items() if v > 0]
    debtors = [(v, u) for u, v in cleaned.items() if v < 0]
    heapq.heapify(creditors)
    heapq.heapify(debtors)
    transfers: list[Transfer] = []
    while creditors and debtors:
        neg_credit, creditor = heapq.heappop(creditors)
        neg_debt, debtor = heapq.heappop(debtors)
        credit, debt = -neg_credit, -neg_debt
        pay = min(credit, debt)
        transfers.append(Transfer(debtor, creditor, pay))
        if credit > pay:
            heapq.heappush(creditors, (-(credit - pay), creditor))
        if debt > pay:
            heapq.heappush(debtors, (-(debt - pay), debtor))
    return transfers


def min_transfers_exact(balances: Mapping[str, int]) -> int:
    values = list(_clean(balances).values())
    m = len(values)
    if m == 0:
        return 0
    if m > 16:
        raise ValueError("exact solver supports at most 16 non-zero balances")
    sums = [0] * (1 << m)
    for mask in range(1, 1 << m):
        low = (mask & -mask).bit_length() - 1
        sums[mask] = sums[mask & (mask - 1)] + values[low]
    best = [0] * (1 << m)
    for mask in range(1, 1 << m):
        best[mask] = max(best[mask ^ (1 << i)] for i in range(m) if mask >> i & 1) + (
            1 if sums[mask] == 0 else 0
        )
    return m - best[-1]


def apply_transfers(balances: Mapping[str, int], transfers: Iterable[Transfer]) -> dict[str, int]:
    result = dict(balances)
    for t in transfers:
        result[t.payer] = result.get(t.payer, 0) + t.amount
        result[t.receiver] = result.get(t.receiver, 0) - t.amount
    return {user: value for user, value in result.items() if value != 0}
