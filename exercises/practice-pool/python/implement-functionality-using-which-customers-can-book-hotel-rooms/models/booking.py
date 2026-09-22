from .base_model import BaseModel
from .customer_session import CustomerSession
from typing import List, Optional


class Booking(BaseModel):
    customer_session: CustomerSession
    booked_rooms: List
    id: Optional[int]

    def __init__(
            self,
            customer_session: CustomerSession,
            booked_rooms: List,
    ):
        super().__init__(id)
        self.customer_session = customer_session
        self.booked_rooms = booked_rooms

