from typing import Optional

from repositories import ParkingSpotRepository
from .spot_assignment_strategy import SpotAssignmentStrategy
from models import ParkingLot, VehicleType, ParkingSpot, ParkingSpotStatus


class RandomSpotAssignmentStrategy(SpotAssignmentStrategy):
    parking_spot_repository: ParkingSpotRepository

    def __init__(
            self,
            parking_spot_repository: ParkingSpotRepository
    ):
        self.parking_spot_repository = parking_spot_repository

    def assign_spot(self, parking_lot: ParkingLot, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        open_spot = self.parking_spot_repository.find_one(
            parking_lot=parking_lot,
            vehicle_type=vehicle_type
        )

        if open_spot is None:
            return None

        open_spot.parking_spot_status = ParkingSpotStatus.OCCUPIED
        self.parking_spot_repository.update(open_spot, open_spot.id)
        return open_spot

