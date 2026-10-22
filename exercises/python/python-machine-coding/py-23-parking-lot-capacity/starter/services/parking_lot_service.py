from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from models.parking_floor import ParkingFloor
from models.vehicle_type import VehicleType


class ParkingLotService(ABC):
    @abstractmethod
    def get_parking_lot_capacity(
        self,
        parking_lot_id: int,
        parking_floors: Optional[List[int]] = None,
        vehicle_types: Optional[List[VehicleType]] = None,
    ) -> Dict[ParkingFloor, Dict[str, int]]:
        pass
