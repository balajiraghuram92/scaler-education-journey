import inspect

import pytest

from insurance.adapters import AutoProtectAdapter, TravelGuardAdapter, TravelInsuranceAdapter
from insurance.model import AutoProtectStatus, ClaimStatus
from insurance.services import AutoProtectApi, TravelGuardApi


class SpyAutoProtect:
    def __init__(self, status="PENDING"):
        self.add_calls = []
        self.status_calls = []
        self.status = status

    def add_claim(self, amount):
        self.add_calls.append(amount)

    def get_status(self, claim_id):
        self.status_calls.append(claim_id)
        return self.status


class SpyTravelGuard:
    def __init__(self, status="PENDING"):
        self.submit_calls = []
        self.status_calls = []
        self.status = status

    def submit_claim(self, claim_id, amount):
        self.submit_calls.append((claim_id, amount))

    def get_claim_status(self, claim_id):
        self.status_calls.append(claim_id)
        return self.status


def auto(spy):
    adapter = AutoProtectAdapter()
    adapter.auto_protect_api = spy
    return adapter


def travel(spy):
    adapter = TravelGuardAdapter()
    adapter.travel_guard_api = spy
    return adapter


def test_interface_is_abstract_with_exactly_two_abstract_methods():
    assert inspect.isabstract(TravelInsuranceAdapter), "TravelInsuranceAdapter must be an ABC with abstract methods"
    assert TravelInsuranceAdapter.__abstractmethods__ == {"add_claim", "get_status"}, (
        f"expected abstract add_claim and get_status, found {sorted(TravelInsuranceAdapter.__abstractmethods__)}"
    )
    with pytest.raises(TypeError):
        TravelInsuranceAdapter()


def test_adapters_wrap_vendor_clients_by_composition():
    a, t = AutoProtectAdapter(), TravelGuardAdapter()
    assert isinstance(a, TravelInsuranceAdapter) and isinstance(t, TravelInsuranceAdapter)
    assert isinstance(a.auto_protect_api, AutoProtectApi), "auto_protect_api must hold an AutoProtectApi"
    assert isinstance(t.travel_guard_api, TravelGuardApi), "travel_guard_api must hold a TravelGuardApi"
    assert not isinstance(a, AutoProtectApi) and not isinstance(t, TravelGuardApi), "do not subclass the vendor clients"


def test_auto_protect_add_claim_drops_the_reference():
    spy = SpyAutoProtect()
    auto(spy).add_claim("ref-1", 250.0)
    assert spy.add_calls == [250.0], "AutoProtect only takes the amount"


def test_travel_guard_add_claim_passes_reference_and_amount():
    spy = SpyTravelGuard()
    travel(spy).add_claim("ref-9", 99.5)
    assert spy.submit_calls == [("ref-9", 99.5)], "TravelGuard takes (claim_id, amount)"


@pytest.mark.parametrize("raw", ["APPROVED", AutoProtectStatus.APPROVED])
def test_auto_protect_approved_maps_for_string_and_enum(raw):
    spy = SpyAutoProtect(raw)
    status = auto(spy).get_status("c1")
    assert status is ClaimStatus.APPROVED, f"{raw!r} must map to ClaimStatus.APPROVED"
    assert spy.status_calls == ["c1"], "the claim reference must be forwarded"


@pytest.mark.parametrize("raw", ["PENDING", "DENIED", AutoProtectStatus.PENDING, AutoProtectStatus.DENIED, "whatever"])
def test_auto_protect_anything_else_is_pending(raw):
    assert auto(SpyAutoProtect(raw)).get_status("c1") is ClaimStatus.PENDING, f"{raw!r} must map to PENDING"


@pytest.mark.parametrize("raw,expected", [
    ("APPROVED", ClaimStatus.APPROVED),
    ("PENDING", ClaimStatus.PENDING),
    ("SUCCESS", ClaimStatus.PENDING),
    ("approved", ClaimStatus.PENDING),
])
def test_travel_guard_status_mapping(raw, expected):
    spy = SpyTravelGuard(raw)
    assert travel(spy).get_status("c7") is expected, f"{raw!r} should map to {expected}"
    assert spy.status_calls == ["c7"]


def test_default_vendor_stubs_work_end_to_end(capsys):
    # The real AutoProtect stub returns an Enum member, which a string-only comparison misses.
    assert AutoProtectAdapter().get_status("x") is ClaimStatus.APPROVED, (
        "the real AutoProtectApi returns AutoProtectStatus.APPROVED; the adapter must normalise it"
    )
    assert TravelGuardAdapter().get_status("x") is ClaimStatus.PENDING
    capsys.readouterr()
