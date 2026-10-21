from typing import List, Optional

class GetParkingLotCapacityRequestDto:
    def __init__(self, parking_lot_id: int, parking_floor_ids: Optional[List[int]] = None, vehicle_types: Optional[List[str]] = None):
        self.parking_lot_id = parking_lot_id
        self.parking_floor_ids = parking_floor_ids
        self.vehicle_types = vehicle_types
