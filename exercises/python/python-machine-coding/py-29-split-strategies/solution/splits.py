from collections.abc import Mapping, Sequence
from decimal import Decimal
from fractions import Fraction


def _check_total(total: int) -> None:
    if type(total) is not int or total <= 0:
        raise ValueError("total must be a positive integer")


def split_equal(total: int, users: Sequence[str]) -> dict[str, int]:
    _check_total(total)
    if not users:
        raise ValueError("users must not be empty")
    if len(set(users)) != len(users):
        raise ValueError("users must be unique")
    base, extra = divmod(total, len(users))
    return {user: base + (1 if i < extra else 0) for i, user in enumerate(users)}


def split_exact(total: int, amounts: Mapping[str, int]) -> dict[str, int]:
    _check_total(total)
    if not amounts:
        raise ValueError("amounts must not be empty")
    for user, amount in amounts.items():
        if type(amount) is not int or amount <= 0:
            raise ValueError(f"amount for {user!r} must be a positive integer")
    if sum(amounts.values()) != total:
        raise ValueError(f"amounts sum to {sum(amounts.values())}, expected {total}")
    return dict(amounts)


def split_percentage(
    total: int, percents: Mapping[str, int | str | Decimal | Fraction]
) -> dict[str, int]:
    _check_total(total)
    if not percents:
        raise ValueError("percents must not be empty")
    users = list(percents)
    pcts: list[Fraction] = []
    for user in users:
        raw = percents[user]
        if isinstance(raw, float):
            raise TypeError("percentages must not be floats; use int, str, Decimal or Fraction")
        pct = Fraction(raw)
        if pct <= 0:
            raise ValueError(f"percentage for {user!r} must be positive")
        pcts.append(pct)
    if sum(pcts) != 100:
        raise ValueError("percentages must sum to exactly 100")

    exact = [Fraction(total) * pct / 100 for pct in pcts]
    floors = [share.numerator // share.denominator for share in exact]
    remainders = [share - floor for share, floor in zip(exact, floors)]
    leftover = total - sum(floors)
    order = sorted(range(len(users)), key=lambda i: (-remainders[i], i))
    for i in order[:leftover]:
        floors[i] += 1
    return dict(zip(users, floors))
