from typing import Optional
from models.base_model import BaseModel
from models.vehicle_type import VehicleType


class Slab(BaseModel):
    """
    Represents a pricing slab used for weekend slab-based fee calculation.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        start_hour: int = 0,
        end_hour: int = -1,
        price: float = 0.0,
        vehicle_type: Optional[VehicleType] = None
    ):
        super().__init__(id)
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.price = price
        self.vehicle_type = vehicle_type
