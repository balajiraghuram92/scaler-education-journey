from collections.abc import Mapping

from parking.design import ParkingLot, ParkingSpot, SpotAssignmentStrategy, VehicleType


class FallbackSpotStrategy(SpotAssignmentStrategy):
    """Try each strategy in order; the first one that finds a spot wins."""

    def __init__(self, *strategies: SpotAssignmentStrategy) -> None:
        if not strategies:
            raise ValueError("at least one strategy is required")
        self._strategies = strategies

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        for strategy in self._strategies:
            spot = strategy.assign(lot, vehicle_type)
            if spot is not None:
                return spot
        return None


class RoutedSpotStrategy(SpotAssignmentStrategy):
    """Choose the strategy by vehicle type, with a default for unlisted types."""

    def __init__(self, routes: Mapping[VehicleType, SpotAssignmentStrategy],
                 default: SpotAssignmentStrategy) -> None:
        self._routes = dict(routes)
        self._default = default

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        return self._routes.get(vehicle_type, self._default).assign(lot, vehicle_type)
