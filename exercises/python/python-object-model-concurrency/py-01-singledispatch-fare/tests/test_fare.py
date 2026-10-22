import pytest

from fare import estimate_fare
from trip import Trip


def test_float_uses_fifteen_per_km():
    assert estimate_fare(10.0) == 150.0, "a float distance costs 15 per km"
    assert estimate_fare(0.5) == 7.5


def test_known_route_codes():
    assert estimate_fare("HSR-AIRPORT") == 600
    assert estimate_fare("MG-AIRPORT") == 550


def test_unknown_route_code_is_free():
    assert estimate_fare("UNKNOWN") == 0, "unknown route codes return 0"
    assert estimate_fare("") == 0, "an empty code is still just an unknown code"


def test_trip_uses_its_distance():
    assert estimate_fare(Trip(20)) == 300, "a Trip costs 15 per km of distance_km"
    assert estimate_fare(Trip(0)) == 0


def test_int_is_not_a_float():
    with pytest.raises(NotImplementedError):
        estimate_fare(10)


def test_bool_and_other_types_fail_loudly():
    for bad in (True, None, [1.0], (1.0,), {"a": 1}):
        with pytest.raises(NotImplementedError):
            estimate_fare(bad)


def test_dispatch_is_registered_with_singledispatch():
    assert hasattr(estimate_fare, "register") and hasattr(estimate_fare, "dispatch"), (
        "estimate_fare must be created with functools.singledispatch"
    )
    registered = set(estimate_fare.registry)
    assert {float, str, Trip} <= registered, f"register float, str and Trip implementations, got {registered}"
    assert int not in registered, "int must not be registered"


def test_subclasses_follow_the_class_hierarchy():
    class Airport(Trip):
        pass

    class Precise(float):
        pass

    assert estimate_fare(Airport(2)) == 30, "a Trip subclass dispatches to the Trip implementation"
    assert estimate_fare(Precise(2.0)) == 30.0, "a float subclass dispatches to the float implementation"
