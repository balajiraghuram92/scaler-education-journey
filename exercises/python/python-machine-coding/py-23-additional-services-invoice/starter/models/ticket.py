from datetime import datetime
from typing import List, Optional

from models.base_model import BaseModel
from models.gate import Gate
from models.parking_attendant import ParkingAttendant
from models.parking_spot import ParkingSpot
from models.vehicle import Vehicle


class Ticket(BaseModel):
    def __init__(
        self,
        vehicle: Vehicle,
        entry_time: datetime,
        parking_spot: ParkingSpot,
        gate: Gate,
        parking_attendant: Optional[ParkingAttendant] = None,
        additional_services: Optional[List] = None,
        id: Optional[int] = None,
    ):
        super().__init__(id)
        self.vehicle = vehicle
        self.entry_time = entry_time
        self.parking_spot = parking_spot
        self.gate = gate
        self.parking_attendant = parking_attendant
        self.additional_services = additional_services if additional_services is not None else []
