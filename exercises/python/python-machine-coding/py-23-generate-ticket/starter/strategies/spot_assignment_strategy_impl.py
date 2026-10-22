from typing import List, Optional, Tuple
from models.floor_status import FloorStatus
from models.parking_floor import ParkingFloor
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.parking_spot_status import ParkingSpotStatus
from models.vehicle_type import VehicleType
from strategies.spot_assignment_strategy import SpotAssignmentStrategy

class SpotAssignmentStrategyImpl(SpotAssignmentStrategy):
    """
    Assigns an available parking spot following these rules:
      1. Only OPERATIONAL floors are considered.
      2. Floor with the least number of available spots for the given vehicle type (> 0) is selected.
      3. In case of a tie, the floor with the lowest floor_number is selected.
      4. On the selected floor, the nearest spot (lowest spot number) is assigned.
      5. The assigned spot's status is updated to OCCUPIED.
      6. If no available spots exist on any operational floor, returns None.
    """

    def assign_spot(self, parking_lot: ParkingLot, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        """Consider only OPERATIONAL floors with at least one AVAILABLE spot supporting vehicle_type. Choose the floor with the fewest such spots (tie: lowest floor_number), take its lowest-numbered such spot, mark it OCCUPIED and return it. Return None when nothing is available."""
        raise NotImplementedError('TODO: implement assign_spot')
