from .base_model import BaseModel
from .coordinator import Coordinator
from .gate_type import GateType
from .parking_lot import ParkingLot


class Gate(BaseModel):
    name: str
    gate_type: GateType
    parking_lot: ParkingLot
    coordinator: Coordinator

    def __init__(self, name: str, gate_type: GateType, parking_lot: ParkingLot, coordinator: Coordinator, id: int = None):
        super().__init__(id)
        self.name = name
        self.gate_type = gate_type
        self.parking_lot = parking_lot
        self.coordinator = coordinator
