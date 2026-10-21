from datetime import datetime
from typing import Optional

from models.base_model import BaseModel
from models.gate import Gate
from models.parking_attendant import ParkingAttendant
from models.ticket import Ticket


class Invoice(BaseModel):
    def __init__(
        self,
        ticket: Ticket,
        gate: Gate,
        parking_attendant: Optional[ParkingAttendant],
        exit_time: datetime,
        amount: float,
        id: Optional[int] = None,
    ):
        super().__init__(id)
        self.ticket = ticket
        self.gate = gate
        self.parking_attendant = parking_attendant
        self.exit_time = exit_time
        self.amount = amount
