from collections.abc import Collection, Iterable
from datetime import datetime


class MissingPriceError(LookupError):
    """No price version applies for the requested key / instant."""


class FeatureNotSupportedError(ValueError):
    """A show asks for features its screen cannot run."""


class PriceBook:
    """Effective-dated prices keyed by (show_id, SEAT_TYPE), amounts in integer minor units.

    Keep one list per key sorted by ``valid_from`` and use ``bisect`` for lookups.
    Seat type names are case-insensitive (store upper-cased); datetimes must be timezone-aware.
    """

    def __init__(self) -> None:
        raise NotImplementedError("Implement PriceBook.__init__")

    def set_price(self, show_id: int, seat_type: str, amount_minor: int, valid_from: datetime) -> None:
        """Insert a price version in any order.

        ValueError for a negative amount, a naive ``valid_from`` or a duplicate ``valid_from`` for the key.
        """
        raise NotImplementedError("Implement set_price")

    def price_at(self, show_id: int, seat_type: str, at: datetime) -> int:
        """Amount of the latest version with ``valid_from <= at``.

        MissingPriceError if there is none; ValueError for a naive ``at``.
        """
        raise NotImplementedError("Implement price_at")

    def total_at(self, show_id: int, seat_types: Iterable[str], at: datetime) -> int:
        """Sum the price of each seat type (repeats allowed).

        If any are unpriced raise ONE MissingPriceError whose message lists all missing types,
        sorted and upper-cased, e.g. ``['PLATINUM', 'RECLINER']``.
        """
        raise NotImplementedError("Implement total_at")


def validate_show_features(
    screen_features: Collection[str], show_features: Collection[str]
) -> frozenset[str]:
    """Upper-case both sides; return the show's features if they are a subset of the screen's.

    Otherwise raise FeatureNotSupportedError naming the unsupported features, sorted.
    """
    raise NotImplementedError("Implement validate_show_features")
