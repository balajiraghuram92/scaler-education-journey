from abc import ABC, abstractmethod
from typing import Optional
from models import ParkingLot, VehicleType, ParkingSpot


class SpotAssignmentStrategy(ABC):
    @abstractmethod
    def assign_spot(self, parking_lot: ParkingLot, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        pass
