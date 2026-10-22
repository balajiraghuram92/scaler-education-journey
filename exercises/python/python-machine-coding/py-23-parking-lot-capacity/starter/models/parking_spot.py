from typing import Optional

from models.base_model import BaseModel
from models.parking_spot_status import ParkingSpotStatus
from models.vehicle_type import VehicleType


class ParkingSpot(BaseModel):
    def __init__(
        self,
        id: Optional[int] = None,
        number: int = 0,
        status: ParkingSpotStatus = ParkingSpotStatus.AVAILABLE,
        supported_vehicle_type: Optional[VehicleType] = None,
    ):
        super().__init__(id)
        self.number = number
        self.status = status
        self.supported_vehicle_type = supported_vehicle_type
