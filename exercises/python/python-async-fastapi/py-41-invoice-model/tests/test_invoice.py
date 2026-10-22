import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from pydantic import ValidationError

from invoice import Invoice, InvoiceLine


def payload(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "currency": "USD",
        "lines": [{"sku": "ABC-0001", "qty": 2, "unitPrice": "19.99"}],
        "discountPct": "10",
        "issuedAt": "2025-01-15T10:00:00+00:00",
    }
    data.update(overrides)
    return data


def line(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"sku": "ABC-0001", "qty": 1, "unitPrice": "1.00"}
    data.update(overrides)
    return data


def test_valid_invoice_totals_and_defaults():
    inv = Invoice.model_validate(payload())
    assert inv.subtotal == Decimal("39.98"), "subtotal is the sum of qty * unit_price"
    assert inv.total == Decimal("35.98"), "total applies the 10% discount"
    no_discount = Invoice.model_validate({k: v for k, v in payload().items() if k != "discountPct"})
    assert no_discount.discount_pct == Decimal("0") and no_discount.total == Decimal("39.98")
    assert isinstance(inv.id, UUID) and inv.id != no_discount.id, "ids are generated per invoice"


def test_camel_case_round_trip_with_string_money():
    inv = Invoice.model_validate(payload())
    data = json.loads(inv.model_dump_json(by_alias=True))
    assert data["issuedAt"].startswith("2025-01-15")
    assert "issued_at" not in data, "by_alias=True must emit camelCase keys"
    assert data["lines"][0]["unitPrice"] == "19.99", "Decimals serialize as strings"
    assert data["total"] == "35.98" and data["subtotal"] == "39.98", "computed fields appear in output"
    # computed fields are output-only: drop them before re-validating against extra="forbid"
    round_trip = inv.model_dump_json(by_alias=True, exclude={"subtotal", "total"})
    assert Invoice.model_validate_json(round_trip).total == inv.total
    by_name = Invoice(
        currency="EUR",
        lines=[InvoiceLine(sku="XYZ-9999", qty=1, unit_price=Decimal("5.00"))],
        issued_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    assert by_name.total == Decimal("5.00"), "populate_by_name=True allows snake_case construction"


def test_total_rounds_half_up_to_two_decimals():
    inv = Invoice.model_validate(payload(lines=[line(unitPrice="10.05")], discountPct="50"))
    assert inv.total == Decimal("5.03"), "5.025 must round half UP to 5.03 (not banker's 5.02)"
    assert inv.total.as_tuple().exponent == -2, "total has exactly two decimal places"


def test_naive_datetime_rejected():
    with pytest.raises(ValidationError) as info:
        Invoice.model_validate(payload(issuedAt="2025-01-15T10:00:00"))
    assert "timezone-aware" in str(info.value)


def test_jpy_requires_whole_prices():
    with pytest.raises(ValidationError):
        Invoice.model_validate(payload(currency="JPY", lines=[line(unitPrice="100.50")]))
    ok = Invoice.model_validate(payload(currency="JPY", lines=[line(unitPrice="100")]))
    assert ok.total == Decimal("90.00")
    assert Invoice.model_validate(payload(currency="USD", lines=[line(unitPrice="100.50")])).currency == "USD"


def test_qty_is_a_strict_positive_int():
    for bad in ("2", 0, -1, 1.0):
        with pytest.raises(ValidationError):
            Invoice.model_validate(payload(lines=[line(qty=bad)]))


def test_unit_price_precision_and_sign():
    for bad in ("19.999", "-0.01", "12345678901.00"):  # 3 decimals, negative, 13 digits in total
        with pytest.raises(ValidationError):
            Invoice.model_validate(payload(lines=[line(unitPrice=bad)]))
    assert Invoice.model_validate(payload(lines=[line(unitPrice="0")])).total == Decimal("0.00")


def test_unknown_and_computed_keys_are_rejected():
    with pytest.raises(ValidationError) as info:
        Invoice.model_validate(payload(bogus=1))
    assert info.value.errors()[0]["loc"] == ("bogus",)
    with pytest.raises(ValidationError):
        Invoice.model_validate(payload(total="1.00")), "clients must not be able to supply derived totals"


def test_error_locations_and_bounds():
    with pytest.raises(ValidationError) as empty:
        Invoice.model_validate(payload(lines=[]))
    assert empty.value.errors()[0]["loc"] == ("lines",)

    with pytest.raises(ValidationError) as sku:
        Invoice.model_validate(payload(lines=[line(sku="abc-1")]))
    assert sku.value.errors()[0]["loc"] == ("lines", 0, "sku")

    for bad in ({"discountPct": "100.01"}, {"discountPct": "-1"}, {"currency": "GBP"}):
        with pytest.raises(ValidationError):
            Invoice.model_validate(payload(**bad))
    assert Invoice.model_validate(payload(discountPct="100")).total == Decimal("0.00")


def test_frozen():
    inv = Invoice.model_validate(payload())
    with pytest.raises(ValidationError):
        inv.currency = "EUR"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        inv.lines[0].qty = 5  # type: ignore[misc]
