from typing import Dict
from models.base_model import BaseModel
from models.customer_session import CustomerSession
from models.room import Room

class Booking(BaseModel):
    def __init__(self):
        super().__init__()
        self.customer_session: CustomerSession = None
        self.booked_rooms: Dict[Room, int] = {}
