from typing import List, Optional
from dtos.get_parking_lot_capacity_request_dto import GetParkingLotCapacityRequestDto
from dtos.get_parking_lot_capacity_response_dto import GetParkingLotCapacityResponseDto
from dtos.response import Response
from dtos.response_status import ResponseStatus
from exceptions.get_parking_lot_request_validation_exception import GetParkingLotRequestValidationException
from exceptions.invalid_parking_lot_exception import InvalidParkingLotException
from models.vehicle_type import VehicleType
from services.parking_lot_service import ParkingLotService

class ParkingLotController:
    """
    The controller for handling requests to get parking lot capacity.
    """

    def __init__(self, parking_lot_service: ParkingLotService):
        """Keep the service."""
        raise NotImplementedError('TODO: implement __init__')

    def get_parking_lot_capacity(self, request: GetParkingLotCapacityRequestDto) -> GetParkingLotCapacityResponseDto:
        """Reject a missing request or a non-positive parking_lot_id, convert vehicle type strings to VehicleType (invalid: error), call the service and return a GetParkingLotCapacityResponseDto wrapping Response(SUCCESS, message) and the map. Any failure returns Response(FAILURE, message) with capacity_map=None."""
        raise NotImplementedError('TODO: implement get_parking_lot_capacity')
