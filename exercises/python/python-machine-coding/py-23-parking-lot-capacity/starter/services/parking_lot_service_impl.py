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
        """Keep the repository."""
        raise NotImplementedError('TODO: implement __init__')

    def get_parking_lot_capacity(self, parking_lot_id: int, parking_floors: Optional[List[int]]=None, vehicle_types: Optional[List[VehicleType]]=None) -> Dict[ParkingFloor, Dict[str, int]]:
        """Raise InvalidParkingLotException for an unknown lot. Filter floors by floor id when parking_floors is given (empty or None means all) and vehicle types when vehicle_types is given (empty or None means all). Return {floor: {vehicle type name: number of AVAILABLE spots of that type}}."""
        raise NotImplementedError('TODO: implement get_parking_lot_capacity')
