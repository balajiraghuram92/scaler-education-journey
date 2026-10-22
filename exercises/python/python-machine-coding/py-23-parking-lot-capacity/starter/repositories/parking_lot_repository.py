from abc import ABC, abstractmethod
from typing import List, Optional

from models.parking_lot import ParkingLot


class ParkingLotRepository(ABC):
    @abstractmethod
    def get_parking_lot_by_gate_id(self, gate_id: int) -> Optional[ParkingLot]:
        pass

    @abstractmethod
    def get_parking_lot_by_id(self, id: int) -> Optional[ParkingLot]:
        pass

    @abstractmethod
    def save(self, parking_lot: ParkingLot) -> ParkingLot:
        pass
