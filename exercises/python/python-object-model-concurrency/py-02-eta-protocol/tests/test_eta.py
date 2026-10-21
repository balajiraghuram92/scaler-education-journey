import pytest

from eta_protocol import ETAProvider
from eta_service import InternalETAProvider, get_eta
from vendor_map import VendorMapETA


def test_protocol_is_runtime_checkable():
    # Without @runtime_checkable, isinstance() against a Protocol raises TypeError.
    assert isinstance(VendorMapETA(), ETAProvider), "ETAProvider must be decorated with @runtime_checkable"


def test_providers_satisfy_the_protocol_without_inheriting():
    for cls in (InternalETAProvider, VendorMapETA):
        assert ETAProvider not in cls.__mro__, f"{cls.__name__} must not inherit from the protocol"
        assert isinstance(cls(), ETAProvider), f"{cls.__name__} must satisfy the protocol structurally"


def test_vendor_provider_returns_42():
    assert VendorMapETA().estimate_minutes("A", "B") == 42.0
    assert get_eta(VendorMapETA(), "Airport", "HSR") == 42.0


def test_internal_provider_formula():
    p = InternalETAProvider()
    expected = abs(hash("Airport") - hash("HSR")) % 60
    assert p.estimate_minutes("Airport", "HSR") == expected, "abs(hash(origin) - hash(destination)) % 60"
    assert 0 <= p.estimate_minutes("X", "Y") < 60
    assert p.estimate_minutes("same", "same") == 0, "identical places are 0 minutes apart"


def test_get_eta_delegates_with_arguments_in_order():
    class Recorder:
        def estimate_minutes(self, origin, destination):
            return f"{origin}->{destination}"

    assert get_eta(Recorder(), "Airport", "HSR") == "Airport->HSR", "get_eta must pass origin then destination"


def test_get_eta_rejects_objects_without_estimate_minutes():
    for bad in (object(), None, "provider", 42, [], type("Almost", (), {"estimate": lambda self, a, b: 1})()):
        with pytest.raises(TypeError):
            get_eta(bad, "A", "B")
