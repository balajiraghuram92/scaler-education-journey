from typing import Dict, Optional
from dtos.response import Response
from models.parking_floor import ParkingFloor

class GetParkingLotCapacityResponseDto:
    def __init__(self, response: Optional[Response] = None, capacity_map: Optional[Dict[ParkingFloor, Dict[str, int]]] = None):
        self.response = response
        self.capacity_map = capacity_map
