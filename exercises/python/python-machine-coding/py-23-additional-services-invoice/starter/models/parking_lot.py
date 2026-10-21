from typing import List, Optional

from models.base_model import BaseModel
from models.gate import Gate
from models.parking_floor import ParkingFloor


class ParkingLot(BaseModel):
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        parking_floors: Optional[List[ParkingFloor]] = None,
        gates: Optional[List[Gate]] = None,
    ):
        super().__init__(id)
        self.name = name
        self.parking_floors = parking_floors if parking_floors is not None else []
        self.gates = gates if gates is not None else []
