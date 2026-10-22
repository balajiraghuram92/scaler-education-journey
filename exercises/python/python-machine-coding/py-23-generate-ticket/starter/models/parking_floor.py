from typing import List, Optional

from models.base_model import BaseModel
from models.floor_status import FloorStatus
from models.parking_spot import ParkingSpot


class ParkingFloor(BaseModel):
    def __init__(
        self,
        id: Optional[int] = None,
        floor_number: int = 0,
        status: FloorStatus = FloorStatus.OPERATIONAL,
        spots: Optional[List[ParkingSpot]] = None,
    ):
        super().__init__(id)
        self.floor_number = floor_number
        self.status = status
        self.spots = spots if spots is not None else []
