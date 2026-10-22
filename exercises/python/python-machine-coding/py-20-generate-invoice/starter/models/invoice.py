from typing import Dict
from models.base_model import BaseModel
from models.room import Room

class Invoice(BaseModel):
    def __init__(self):
        super().__init__()
        self.booked_rooms: Dict[Room, int] = {}
        self.total_amount: float = 0.0
        self.gst: float = 0.0
        self.service_charge: float = 0.0
