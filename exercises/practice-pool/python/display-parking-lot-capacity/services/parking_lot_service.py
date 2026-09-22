from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

from models import VehicleType, Ticket, ParkingFloor


class ParkingLotService(ABC):

    @abstractmethod
    def get_parking_lot_capacity(
            self,
            parking_lot_id: int,
            parking_floor_ids: List[int] = None,
            vehicle_types: List[VehicleType] = None,
            ) -> Dict[ParkingFloor, Dict[VehicleType, int]]:
        pass
