from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict

from models import VehicleType, ParkingFloor


class ResponseStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class GetParkingLotCapacityRequestDto:
    parking_lot_id: int
    parking_floor_ids: Optional[List[int]] = field(default=None)
    vehicle_types: Optional[List[VehicleType]] = field(default=None)


@dataclass
class GetParkingLotCapacityResponseDto:
    response_status: ResponseStatus
    capacity: Optional[Dict[ParkingFloor, Dict[VehicleType, int]]] = field(default=None)
