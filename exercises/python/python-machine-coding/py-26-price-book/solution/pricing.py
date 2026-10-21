from bisect import bisect_left, bisect_right
from collections.abc import Collection, Iterable
from datetime import datetime


class MissingPriceError(LookupError):
    pass


class FeatureNotSupportedError(ValueError):
    pass


def _require_aware(value: datetime, name: str) -> None:
    if value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


class PriceBook:
    def __init__(self) -> None:
        self._versions: dict[tuple[int, str], list[tuple[datetime, int]]] = {}

    def set_price(
        self, show_id: int, seat_type: str, amount_minor: int, valid_from: datetime
    ) -> None:
        if amount_minor < 0:
            raise ValueError("amount_minor must not be negative")
        _require_aware(valid_from, "valid_from")
        rows = self._versions.setdefault((show_id, seat_type.upper()), [])
        i = bisect_left(rows, valid_from, key=lambda row: row[0])
        if i < len(rows) and rows[i][0] == valid_from:
            raise ValueError("a price with this valid_from already exists")
        rows.insert(i, (valid_from, amount_minor))

    def price_at(self, show_id: int, seat_type: str, at: datetime) -> int:
        _require_aware(at, "at")
        key = (show_id, seat_type.upper())
        rows = self._versions.get(key, [])
        i = bisect_right(rows, at, key=lambda row: row[0])
        if i == 0:
            raise MissingPriceError(f"no price for show {show_id}, seat type {key[1]}")
        return rows[i - 1][1]

    def total_at(self, show_id: int, seat_types: Iterable[str], at: datetime) -> int:
        total = 0
        missing: set[str] = set()
        for seat_type in seat_types:
            try:
                total += self.price_at(show_id, seat_type, at)
            except MissingPriceError:
                missing.add(seat_type.upper())
        if missing:
            raise MissingPriceError(f"no price for seat types: {sorted(missing)}")
        return total


def validate_show_features(
    screen_features: Collection[str], show_features: Collection[str]
) -> frozenset[str]:
    supported = {f.upper() for f in screen_features}
    requested = frozenset(f.upper() for f in show_features)
    unsupported = requested - supported
    if unsupported:
        raise FeatureNotSupportedError(f"screen cannot run: {sorted(unsupported)}")
    return requested
