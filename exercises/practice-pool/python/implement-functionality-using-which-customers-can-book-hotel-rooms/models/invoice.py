from typing import List, Optional

from .base_model import BaseModel


class Invoice(BaseModel):
    booked_rooms: List
    total_amount: float
    gst: float
    service_charge: float

    def __init__(
            self,
            booked_rooms: List = None,
            total_amount: float = 0.0,
            gst: float = 0.0,
            service_charge: float = 0.0,
            id: Optional[int] = None
    ):
        super().__init__(id)
        if booked_rooms is None:
            booked_rooms = []
        self.booked_rooms = booked_rooms
        self.total_amount = total_amount
        self.gst = gst
        self.service_charge = service_charge