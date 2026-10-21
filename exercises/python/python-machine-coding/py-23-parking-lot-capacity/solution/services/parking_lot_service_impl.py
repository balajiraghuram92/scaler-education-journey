from typing import Dict, List, Optional
from exceptions.invalid_parking_lot_exception import InvalidParkingLotException
from models.parking_floor import ParkingFloor
from models.parking_spot_status import ParkingSpotStatus
from models.vehicle_type import VehicleType
from repositories.parking_lot_repository import ParkingLotRepository
from services.parking_lot_service import ParkingLotService


class ParkingLotServiceImpl(ParkingLotService):
    """
    Implementation of the ParkingLotService that calculates the capacity of a parking lot.
    """

    def __init__(self, parking_lot_repository: ParkingLotRepository):
        self.parking_lot_repository = parking_lot_repository

    def get_parking_lot_capacity(
        self,
        parking_lot_id: int,
        parking_floors: Optional[List[int]] = None,
        vehicle_types: Optional[List[VehicleType]] = None
    ) -> Dict[ParkingFloor, Dict[str, int]]:
        """
        Calculates the available parking spot capacity for a parking lot,
        filtered optionally by parking floor IDs and vehicle types.

        :param parking_lot_id: ID of the parking lot.
        :param parking_floors: Optional list of floor IDs to filter by. If None or empty, all floors are considered.
        :param vehicle_types: Optional list of VehicleType enums to filter by. If None or empty, all types are considered.
        :return: A dictionary mapping ParkingFloor to a dictionary of vehicle type name -> available spot count.
        :raises InvalidParkingLotException: If the parking lot with the given ID is not found.
        """
        # Step 1: Look up the parking lot
        parking_lot = self.parking_lot_repository.get_parking_lot_by_id(parking_lot_id)
        if parking_lot is None:
            raise InvalidParkingLotException(f"Parking lot with id {parking_lot_id} does not exist.")

        # Step 2: Determine floors to inspect
        if parking_floors:
            floor_id_set = set(parking_floors)
            floors_to_consider = [
                floor for floor in (parking_lot.parking_floors or [])
                if floor.id in floor_id_set
            ]
        else:
            floors_to_consider = parking_lot.parking_floors or []

        # Step 3: Determine vehicle types to inspect
        if vehicle_types:
            types_to_consider = [
                vt.name if isinstance(vt, VehicleType) else str(vt)
                for vt in vehicle_types
            ]
        else:
            types_to_consider = [vt.name for vt in VehicleType]

        # Preserve order while ensuring uniqueness
        unique_vehicle_types = list(dict.fromkeys(types_to_consider))

        # Step 4: Calculate available capacity per floor per vehicle type
        capacity_map: Dict[ParkingFloor, Dict[str, int]] = {}

        for floor in floors_to_consider:
            counts = {vt_name: 0 for vt_name in unique_vehicle_types}
            for spot in (floor.spots or []):
                # Only available spots contribute to capacity
                if spot.status == ParkingSpotStatus.AVAILABLE:
                    spot_vt_name = (
                        spot.supported_vehicle_type.name
                        if isinstance(spot.supported_vehicle_type, VehicleType)
                        else str(spot.supported_vehicle_type)
                    )
                    if spot_vt_name in counts:
                        counts[spot_vt_name] += 1

            capacity_map[floor] = counts

        return capacity_map
