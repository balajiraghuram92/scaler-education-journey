from collections.abc import Mapping, Sequence
from decimal import Decimal
from fractions import Fraction


def split_equal(total: int, users: Sequence[str]) -> dict[str, int]:
    """Split ``total`` minor units equally; the ``divmod`` remainder goes one unit each to the FIRST users.

    ``users`` must be non-empty and unique; ``total`` a positive ``int`` (not bool/float). ValueError otherwise.
    Result preserves the order of ``users``.
    """
    raise NotImplementedError("Implement split_equal")


def split_exact(total: int, amounts: Mapping[str, int]) -> dict[str, int]:
    """Each amount a positive ``int`` and the amounts must sum to ``total``, else ValueError."""
    raise NotImplementedError("Implement split_exact")


def split_percentage(
    total: int, percents: Mapping[str, int | str | Decimal | Fraction]
) -> dict[str, int]:
    """Largest-remainder split using exact ``Fraction`` arithmetic.

    - ``float`` percentages raise TypeError
    - percentages must be positive and sum to exactly 100, else ValueError
    - everyone gets floor(total * pct / 100); leftover units go one each to the largest fractional
      remainders, ties broken by order of appearance in ``percents``
    """
    raise NotImplementedError("Implement split_percentage")
