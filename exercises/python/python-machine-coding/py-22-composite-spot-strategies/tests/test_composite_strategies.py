import random

import pytest

from parking.composite_strategies import FallbackSpotStrategy, RoutedSpotStrategy
from parking.design import (
    FloorStatus,
    LeastAvailableFloorStrategy,
    NearestSpotStrategy,
    ParkingFloor,
    ParkingLot,
    ParkingSpot,
    SpotAssignmentStrategy,
    SpotStatus,
    VehicleType,
)


def random_lot(rng):
    floors = []
    for number in range(rng.randint(1, 4)):
        spots = [ParkingSpot(i, rng.choice(list(VehicleType)), rng.choice(list(SpotStatus)))
                 for i in range(1, rng.randint(1, 8))]
        status = rng.choice([FloorStatus.OPERATIONAL, FloorStatus.OPERATIONAL, FloorStatus.UNDER_MAINTENANCE])
        floors.append(ParkingFloor(number, spots, status))
    return ParkingLot("random", floors, [])


def statuses(lot):
    return [s.status for f in lot.floors for s in f.spots]


class Counting(SpotAssignmentStrategy):
    def __init__(self, result=None):
        self.result = result
        self.calls = 0

    def assign(self, lot, vehicle_type):
        self.calls += 1
        return self.result


def one_spot_lot(vehicle_type=VehicleType.CAR):
    spot = ParkingSpot(1, vehicle_type)
    return ParkingLot("t", [ParkingFloor(0, [spot])], []), spot


NAMES = ["nearest", "least", "fallback", "routed"]


def strategies():
    return {
        "nearest": NearestSpotStrategy(),
        "least": LeastAvailableFloorStrategy(),
        "fallback": FallbackSpotStrategy(LeastAvailableFloorStrategy(), NearestSpotStrategy()),
        "routed": RoutedSpotStrategy({VehicleType.TRUCK: NearestSpotStrategy()}, LeastAvailableFloorStrategy()),
    }


@pytest.mark.parametrize("name", NAMES)
def test_every_strategy_satisfies_the_assignment_invariants(name):
    strategy, rng = strategies()[name], random.Random(5)
    for _ in range(300):
        lot = random_lot(rng)
        for vehicle_type in VehicleType:
            before = statuses(lot)
            spot = strategy.assign(lot, vehicle_type)
            assert statuses(lot) == before, f"{name} must be read-only"
            usable = [s for f in lot.floors if f.status is FloorStatus.OPERATIONAL for s in f.spots
                      if s.status is SpotStatus.AVAILABLE and s.supported_vehicle_type is vehicle_type]
            if not usable:
                assert spot is None, f"{name} returned a spot although none is usable"
            else:
                assert any(spot is s for s in usable), f"{name} returned a spot that is not usable"


def test_fallback_uses_the_second_strategy_only_when_the_first_finds_nothing():
    lot, spot = one_spot_lot()
    first, second = Counting(None), Counting(spot)
    assert FallbackSpotStrategy(first, second).assign(lot, VehicleType.CAR) is spot
    assert (first.calls, second.calls) == (1, 1)
    winner, backup = Counting(spot), Counting(None)
    assert FallbackSpotStrategy(winner, backup).assign(lot, VehicleType.CAR) is spot
    assert backup.calls == 0, "later strategies must not be consulted once a spot is found"


def test_fallback_requires_at_least_one_strategy():
    with pytest.raises(ValueError):
        FallbackSpotStrategy()


def test_fallback_returns_none_when_every_strategy_finds_nothing():
    lot, _ = one_spot_lot()
    a, b = Counting(None), Counting(None)
    assert FallbackSpotStrategy(a, b).assign(lot, VehicleType.CAR) is None
    assert (a.calls, b.calls) == (1, 1)


def test_fallback_order_decides_the_winner():
    lot, spot = one_spot_lot()
    other = ParkingSpot(9, VehicleType.CAR)
    assert FallbackSpotStrategy(Counting(spot), Counting(other)).assign(lot, VehicleType.CAR) is spot
    assert FallbackSpotStrategy(Counting(other), Counting(spot)).assign(lot, VehicleType.CAR) is other


def test_routed_picks_strategy_by_vehicle_type():
    lot, spot = one_spot_lot()
    truck_strategy, default = Counting(spot), Counting(None)
    routed = RoutedSpotStrategy({VehicleType.TRUCK: truck_strategy}, default)
    assert routed.assign(lot, VehicleType.TRUCK) is spot
    assert (truck_strategy.calls, default.calls) == (1, 0)


def test_routed_uses_default_for_unlisted_types():
    lot, spot = one_spot_lot()
    default = Counting(spot)
    routed = RoutedSpotStrategy({VehicleType.TRUCK: Counting(None)}, default)
    assert routed.assign(lot, VehicleType.BIKE) is spot
    assert default.calls == 1


def test_routed_only_consults_the_chosen_strategy():
    lot, spot = one_spot_lot()
    a, b, default = Counting(spot), Counting(spot), Counting(spot)
    routed = RoutedSpotStrategy({VehicleType.CAR: a, VehicleType.BIKE: b}, default)
    routed.assign(lot, VehicleType.CAR)
    assert (a.calls, b.calls, default.calls) == (1, 0, 0)


def test_composites_are_spot_assignment_strategies():
    fallback = FallbackSpotStrategy(NearestSpotStrategy())
    routed = RoutedSpotStrategy({}, fallback)
    assert isinstance(fallback, SpotAssignmentStrategy) and isinstance(routed, SpotAssignmentStrategy)
    lot, spot = one_spot_lot()
    assert FallbackSpotStrategy(routed).assign(lot, VehicleType.CAR) is spot, "composites must nest"


def test_spots_in_maintenance_floors_are_never_returned():
    spot = ParkingSpot(1, VehicleType.CAR)
    lot = ParkingLot("t", [ParkingFloor(0, [spot], FloorStatus.UNDER_MAINTENANCE)], [])
    for strategy in strategies().values():
        assert strategy.assign(lot, VehicleType.CAR) is None
