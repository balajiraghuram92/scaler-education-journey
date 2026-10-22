from typing import Optional

from models.base_model import BaseModel
from models.vehicle_type import VehicleType


class Vehicle(BaseModel):
    def __init__(self, registration_number: str, vehicle_type: VehicleType, id: Optional[int] = None):
        super().__init__(id)
        self.registration_number = registration_number
        self.vehicle_type = vehicle_type
