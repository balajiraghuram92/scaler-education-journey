from collections.abc import Mapping
from parking.design import ParkingLot, ParkingSpot, SpotAssignmentStrategy, VehicleType

class FallbackSpotStrategy(SpotAssignmentStrategy):
    """Try each strategy in order; the first one that finds a spot wins."""

    def __init__(self, *strategies: SpotAssignmentStrategy) -> None:
        """Keep the strategies in order. With no strategies raise ValueError."""
        raise NotImplementedError('TODO: implement __init__')

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        """Ask each strategy in order and return the first spot that is not None; None if all return None."""
        raise NotImplementedError('TODO: implement assign')

class RoutedSpotStrategy(SpotAssignmentStrategy):
    """Choose the strategy by vehicle type, with a default for unlisted types."""

    def __init__(self, routes: Mapping[VehicleType, SpotAssignmentStrategy], default: SpotAssignmentStrategy) -> None:
        """Keep a copy of the routes mapping and the default strategy."""
        raise NotImplementedError('TODO: implement __init__')

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        """Delegate to routes[vehicle_type], or to the default strategy when the type is not listed."""
        raise NotImplementedError('TODO: implement assign')
