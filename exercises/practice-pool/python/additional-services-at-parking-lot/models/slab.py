from .base_model import BaseModel
from .vehicle_type import VehicleType


class Slab(BaseModel):
    start_hour: int
    end_hour: int
    price: float
    vehicle_type: VehicleType
