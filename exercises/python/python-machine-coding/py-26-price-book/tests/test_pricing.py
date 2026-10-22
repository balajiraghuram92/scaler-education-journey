from datetime import datetime, timezone

import pytest

from pricing import (
    FeatureNotSupportedError,
    MissingPriceError,
    PriceBook,
    validate_show_features,
)

UTC = timezone.utc


def at(day: int, hour: int = 0) -> datetime:
    return datetime(2026, 11, day, hour, tzinfo=UTC)


def make_book() -> PriceBook:
    book = PriceBook()
    # inserted out of order on purpose
    book.set_price(7, "gold", 30000, at(8))
    book.set_price(7, "GOLD", 25000, at(1))
    book.set_price(7, "silver", 15000, at(1))
    return book


def test_latest_version_at_or_before_the_instant_wins():
    book = make_book()
    assert book.price_at(7, "Gold", at(3)) == 25000
    assert book.price_at(7, "gold", at(8)) == 30000
    assert book.price_at(7, "gold", at(8, 5)) == 30000


def test_before_first_version_or_unknown_key_is_missing():
    book = make_book()
    with pytest.raises(MissingPriceError):
        book.price_at(7, "gold", datetime(2026, 10, 31, 23, tzinfo=UTC))
    with pytest.raises(MissingPriceError):
        book.price_at(8, "gold", at(3))


def test_total_sums_with_repeats():
    book = make_book()
    assert book.total_at(7, ["gold", "gold", "silver"], at(9)) == 30000 * 2 + 15000


def test_total_reports_all_missing_types_at_once():
    book = make_book()
    with pytest.raises(MissingPriceError, match=r"\['PLATINUM', 'RECLINER'\]"):
        book.total_at(7, ["gold", "recliner", "platinum"], at(9))


def test_validation_of_inputs():
    book = PriceBook()
    with pytest.raises(ValueError):
        book.set_price(1, "gold", -1, at(1))
    with pytest.raises(ValueError):
        book.set_price(1, "gold", 100, datetime(2026, 11, 1))  # naive
    book.set_price(1, "gold", 100, at(1))
    with pytest.raises(ValueError):
        book.set_price(1, "GOLD", 200, at(1))  # same valid_from
    with pytest.raises(ValueError):
        book.price_at(1, "gold", datetime(2026, 11, 2))  # naive lookup


def test_validate_show_features():
    assert validate_show_features({"3d", "dolby_audio"}, {"3D"}) == frozenset({"3D"})
    assert validate_show_features(["3D"], []) == frozenset()
    with pytest.raises(FeatureNotSupportedError, match=r"\['ATMOS', 'IMAX'\]"):
        validate_show_features({"3D"}, {"imax", "atmos", "3d"})


def test_exact_boundary_instant_uses_the_new_version():
    book = make_book()
    assert book.price_at(7, "gold", at(7, 23)) == 25000, "one hour before the change the old price applies"
    assert book.price_at(7, "gold", at(8)) == 30000, "valid_from is inclusive"


def test_prices_are_independent_per_show_and_seat_type():
    book = make_book()
    book.set_price(8, "gold", 99900, at(1))
    assert book.price_at(7, "gold", at(2)) == 25000
    assert book.price_at(8, "gold", at(2)) == 99900
    assert book.price_at(7, "silver", at(2)) == 15000


def test_aware_datetimes_in_different_zones_compare_by_instant():
    from datetime import timedelta

    ist = timezone(timedelta(hours=5, minutes=30))
    book = PriceBook()
    book.set_price(1, "gold", 100, datetime(2026, 11, 1, 5, 30, tzinfo=ist))  # == 00:00 UTC
    assert book.price_at(1, "gold", datetime(2026, 11, 1, 0, 0, tzinfo=UTC)) == 100
    with pytest.raises(MissingPriceError):
        book.price_at(1, "gold", datetime(2026, 10, 31, 23, 59, tzinfo=UTC))


def test_zero_price_is_allowed_and_total_of_nothing_is_zero():
    book = PriceBook()
    book.set_price(1, "free", 0, at(1))
    assert book.price_at(1, "free", at(2)) == 0
    assert book.total_at(1, [], at(2)) == 0
