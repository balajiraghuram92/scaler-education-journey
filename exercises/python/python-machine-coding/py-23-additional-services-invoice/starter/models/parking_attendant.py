from typing import Optional

from models.base_model import BaseModel


class ParkingAttendant(BaseModel):
    def __init__(self, id: Optional[int] = None, name: str = ""):
        super().__init__(id)
        self.name = name
