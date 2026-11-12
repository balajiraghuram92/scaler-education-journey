"""format_dotnet_datetime matches System.Text.Json UTC output (no database)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.base import format_dotnet_datetime


def test_no_fraction_when_microsecond_zero() -> None:
    value = datetime(2026, 11, 2, 0, 15, 2, tzinfo=UTC)
    assert format_dotnet_datetime(value) == "2026-11-02T00:15:02Z"


def test_six_significant_digits_kept() -> None:
    value = datetime(2026, 11, 2, 0, 15, 2, 705684, tzinfo=UTC)
    assert format_dotnet_datetime(value) == "2026-11-02T00:15:02.705684Z"


def test_trailing_zeros_stripped() -> None:
    value = datetime(2026, 11, 2, 0, 15, 2, 705680, tzinfo=UTC)
    assert format_dotnet_datetime(value) == "2026-11-02T00:15:02.70568Z"


def test_naive_datetime_has_no_suffix() -> None:
    assert format_dotnet_datetime(datetime(1, 1, 1)) == "0001-01-01T00:00:00"
