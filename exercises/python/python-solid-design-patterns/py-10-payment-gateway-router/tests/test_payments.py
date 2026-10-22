import dataclasses
import inspect
from decimal import Decimal

import pytest

from payments import Charge, CheckoutService, ConfigurationError


class FakeGateway:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[tuple[Decimal, str, str]] = []

    def charge(self, amount: Decimal, currency: str, customer_id: str) -> Charge:
        self.calls.append((amount, currency, customer_id))
        return Charge(self.name, amount, currency, customer_id)


def make_service():
    razorpay, stripe = FakeGateway("razorpay"), FakeGateway("stripe")
    service = CheckoutService(
        gateways={"razorpay": razorpay, "stripe": stripe},
        routes={"IN": "razorpay", "DE": "stripe", "FR": "stripe"},
        default="stripe",
    )
    return service, razorpay, stripe


def test_routes_by_country():
    service, razorpay, stripe = make_service()
    assert service.checkout("IN", Decimal("10"), "INR", "c1").gateway == "razorpay"
    assert service.checkout("DE", Decimal("10"), "EUR", "c2").gateway == "stripe"
    assert len(razorpay.calls) == 1 and len(stripe.calls) == 1, "each gateway should be called exactly once"
    assert razorpay.calls[0] == (Decimal("10"), "INR", "c1"), "arguments must be passed through unchanged"


def test_unknown_country_uses_default():
    service, _, _ = make_service()
    assert service.gateway_for("BR") == "stripe"


def test_country_lookup_is_case_insensitive():
    service, _, _ = make_service()
    assert service.gateway_for("in") == "razorpay"
    assert service.gateway_for("De") == "stripe"


def test_rejects_non_positive_amount_without_calling_gateway():
    service, razorpay, stripe = make_service()
    for bad in (Decimal("0"), Decimal("-5")):
        with pytest.raises(ValueError):
            service.checkout("IN", bad, "INR", "c1")
    assert razorpay.calls == [] and stripe.calls == [], "no gateway may be called for an invalid amount"


def test_unknown_gateway_in_config_fails_fast():
    with pytest.raises(ConfigurationError):
        CheckoutService({"stripe": FakeGateway("stripe")}, {"IN": "razorpay"}, default="stripe")
    with pytest.raises(ConfigurationError):
        CheckoutService({"stripe": FakeGateway("stripe")}, {}, default="paypal")


def test_new_gateway_needs_no_change_to_service():
    class AdyenGateway:
        def charge(self, amount, currency, customer_id):
            return Charge("adyen", amount, currency, customer_id)

    service = CheckoutService({"adyen": AdyenGateway()}, {"NL": "adyen"}, default="adyen")
    assert service.checkout("NL", Decimal("5"), "EUR", "c9").gateway == "adyen"


def test_caller_mutating_inputs_after_construction_has_no_effect():
    razorpay, stripe = FakeGateway("razorpay"), FakeGateway("stripe")
    gateways = {"razorpay": razorpay, "stripe": stripe}
    routes = {"IN": "razorpay"}
    service = CheckoutService(gateways, routes, default="stripe")
    routes["IN"] = "stripe"
    gateways.clear()
    assert service.checkout("IN", Decimal("1"), "INR", "c1").gateway == "razorpay", "take defensive copies of the mappings"


def test_charge_is_frozen_and_service_names_no_concrete_gateway():
    charge = Charge("stripe", Decimal("1"), "EUR", "c1")
    with pytest.raises(dataclasses.FrozenInstanceError):
        charge.amount = Decimal("2")
    source = inspect.getsource(CheckoutService).lower()
    for concrete in ("razorpay", "stripe", "adyen", "paypal"):
        assert concrete not in source, f"CheckoutService must not name the concrete gateway {concrete!r}"
