import inspect
from types import SimpleNamespace

import pytest

from pricing.manager import PricingManager
from pricing.model import RideDetails
from pricing.strategies import (
    DistanceBasedPricingStrategy,
    PricingStrategy,
    SurgePricingStrategy,
    TimeBasedPricingStrategy,
)

CONCRETE = (DistanceBasedPricingStrategy, TimeBasedPricingStrategy, SurgePricingStrategy)


def test_interface_is_abstract_and_declares_calculate_price():
    assert inspect.isabstract(PricingStrategy), "PricingStrategy must be an ABC with an abstract method"
    assert "calculate_price" in PricingStrategy.__abstractmethods__
    with pytest.raises(TypeError):
        PricingStrategy()


def test_each_rule_is_its_own_strategy_subclass():
    for cls in CONCRETE:
        assert issubclass(cls, PricingStrategy), f"{cls.__name__} must subclass PricingStrategy"
        assert not inspect.isabstract(cls), f"{cls.__name__} must implement calculate_price"
    assert len({c.__name__ for c in CONCRETE}) == 3


def test_distance_based_price():
    s = DistanceBasedPricingStrategy()
    assert s.calculate_price(RideDetails(distance=10.0, duration=99.0)) == 25.0, "5.0 + 2.0 * 10 km"
    assert s.calculate_price(RideDetails(distance=0.0, duration=5.0)) == 5.0, "a zero-distance ride still costs the base fare"


def test_time_based_price():
    s = TimeBasedPricingStrategy()
    assert s.calculate_price(RideDetails(distance=99.0, duration=20.0)) == 15.0, "5.0 + 0.5 * 20 min"
    assert s.calculate_price(RideDetails(distance=1.0, duration=0.0)) == 5.0


def test_surge_price_ignores_distance_and_duration():
    s = SurgePricingStrategy()
    assert s.calculate_price(RideDetails(distance=1.0, duration=1.0)) == 10.0, "5.0 * 2.0"
    assert s.calculate_price(RideDetails(distance=500.0, duration=900.0)) == 10.0


def test_strategies_only_read_the_attributes_they_need():
    assert DistanceBasedPricingStrategy().calculate_price(SimpleNamespace(distance=3.0)) == 11.0
    assert TimeBasedPricingStrategy().calculate_price(SimpleNamespace(duration=4.0)) == 7.0
    assert SurgePricingStrategy().calculate_price(SimpleNamespace()) == 10.0


def test_manager_delegates_to_the_injected_strategy():
    seen = []

    class Spy(PricingStrategy):
        def calculate_price(self, ride_details):
            seen.append(ride_details)
            return 42.5

    ride = RideDetails(1.0, 2.0)
    assert PricingManager(Spy()).calculate_price(ride) == 42.5, "return exactly what the strategy returns"
    assert seen == [ride] and seen[0] is ride, "the same ride must be passed through"


def test_manager_has_no_hard_coded_rules_and_accepts_new_strategies():
    for name in ("BASE_FARE", "PER_KILOMETER_RATE", "PER_MINUTE_RATE", "SURGE_MULTIPLIER"):
        assert not hasattr(PricingManager, name), f"PricingManager must not keep the constant {name}"

    class FlatRate(PricingStrategy):
        def calculate_price(self, ride_details):
            return 7.0

    ride = RideDetails(10.0, 20.0)
    prices = [PricingManager(s).calculate_price(ride) for s in
              (DistanceBasedPricingStrategy(), TimeBasedPricingStrategy(), SurgePricingStrategy(), FlatRate())]
    assert prices == [25.0, 15.0, 10.0, 7.0], f"each strategy must drive the manager; got {prices}"
