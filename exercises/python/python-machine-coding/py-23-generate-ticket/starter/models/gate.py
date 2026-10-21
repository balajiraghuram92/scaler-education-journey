from typing import Optional

from models.base_model import BaseModel
from models.gate_type import GateType
from models.parking_attendant import ParkingAttendant


class Gate(BaseModel):
    def __init__(
        self,
        id: Optional[int] = None,
        gate_number: int = 0,
        gate_type: Optional[GateType] = None,
        parking_attendant: Optional[ParkingAttendant] = None,
    ):
        super().__init__(id)
        self.gate_number = gate_number
        self.gate_type = gate_type
        self.parking_attendant = parking_attendant
