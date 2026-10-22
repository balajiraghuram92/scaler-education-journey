from typing import Optional, Dict
from models.floor_status import FloorStatus
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.parking_spot_status import ParkingSpotStatus
from models.vehicle_type import VehicleType
from strategies.spot_assignment_strategy import SpotAssignmentStrategy


class EqualDistributionAssignmentStrategy(SpotAssignmentStrategy):
    """
    Strategy that distributes vehicles across operational floors by picking the floor
    with the maximum number of available spots for the given vehicle type.
    """

    def assign_spot(self, parking_lot: ParkingLot, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        # Count available spots per floor
        floor_distribution: Dict[int, int] = {}
        for floor in parking_lot.parking_floors:
            if floor.status == FloorStatus.OPERATIONAL:
                for spot in floor.spots:
                    if spot.status == ParkingSpotStatus.AVAILABLE and spot.supported_vehicle_type == vehicle_type:
                        floor_distribution[floor.id] = floor_distribution.get(floor.id, 0) + 1

        if not floor_distribution:
            return None

        # Find the floor with the maximum number of available spots
        max_floor_id = -1
        max_spots = -1
        for floor_id, count in floor_distribution.items():
            if count > max_spots:
                max_spots = count
                max_floor_id = floor_id

        # Find the selected floor and pick its first available spot
        selected_floor = next((f for f in parking_lot.parking_floors if f.id == max_floor_id), None)
        if selected_floor is not None:
            for spot in selected_floor.spots:
                if spot.status == ParkingSpotStatus.AVAILABLE and spot.supported_vehicle_type == vehicle_type:
                    spot.status = ParkingSpotStatus.OCCUPIED
                    return spot

        return None
