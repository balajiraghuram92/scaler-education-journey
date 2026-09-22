from .base_model import BaseModel
from .vehicle_type import VehicleType


class Vehicle(BaseModel):
    number_plate: str
    vehicle_type: VehicleType

    def __init__(self, number_plate: str, vehicle_type: VehicleType, id: int = None):
        super().__init__(id)
        self.number_plate = number_plate
        self.vehicle_type = vehicle_type
