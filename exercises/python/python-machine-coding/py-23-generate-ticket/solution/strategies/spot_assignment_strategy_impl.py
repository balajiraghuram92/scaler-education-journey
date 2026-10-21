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
        if not parking_lot or not parking_lot.parking_floors:
            return None

        # Candidate floors with at least one available spot for this vehicle type
        candidates: List[Tuple[ParkingFloor, List[ParkingSpot]]] = []

        for floor in parking_lot.parking_floors:
            # Rule 3: Only operational floors are considered
            if floor.status != FloorStatus.OPERATIONAL:
                continue

            available_spots = [
                spot for spot in (floor.spots or [])
                if spot.status == ParkingSpotStatus.AVAILABLE and spot.supported_vehicle_type == vehicle_type
            ]

            if available_spots:
                candidates.append((floor, available_spots))

        if not candidates:
            return None

        # Rule 1 & 2: Least number of available spots, tie-break by lowest floor number
        candidates.sort(key=lambda item: (len(item[1]), item[0].floor_number))

        selected_floor, spots_on_floor = candidates[0]

        # Rule 4: Nearest spot on that floor (lowest spot number)
        spots_on_floor.sort(key=lambda s: s.number)
        selected_spot = spots_on_floor[0]

        # Update status to OCCUPIED
        selected_spot.status = ParkingSpotStatus.OCCUPIED
        return selected_spot
