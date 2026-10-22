from typing import Optional
from models.floor_status import FloorStatus
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.parking_spot_status import ParkingSpotStatus
from models.vehicle_type import VehicleType
from strategies.spot_assignment_strategy import SpotAssignmentStrategy


class AssignNearestAvailableSpotStrategy(SpotAssignmentStrategy):
    """
    Strategy that assigns the first available spot matching the vehicle type
    on the first operational floor.
    """

    def assign_spot(self, parking_lot: ParkingLot, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        for floor in parking_lot.parking_floors:
            if floor.status == FloorStatus.OPERATIONAL:
                for spot in floor.spots:
                    if spot.status == ParkingSpotStatus.AVAILABLE and spot.supported_vehicle_type == vehicle_type:
                        spot.status = ParkingSpotStatus.OCCUPIED
                        return spot
        return None
