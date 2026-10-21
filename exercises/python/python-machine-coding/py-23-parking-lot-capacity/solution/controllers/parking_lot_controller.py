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
        self.parking_lot_service = parking_lot_service

    def get_parking_lot_capacity(self, request: GetParkingLotCapacityRequestDto) -> GetParkingLotCapacityResponseDto:
        """
        Handles requests to calculate parking lot capacity based on filters.
        """
        try:
            # Step 1: Validate request object and ID
            if request is None:
                raise GetParkingLotRequestValidationException("Request cannot be None")

            if request.parking_lot_id is None or request.parking_lot_id <= 0:
                raise GetParkingLotRequestValidationException("Parking lot ID must be a positive integer")

            # Step 2: Convert vehicle type strings to VehicleType enums if provided
            vehicle_types: Optional[List[VehicleType]] = None
            if request.vehicle_types is not None:
                vehicle_types = []
                for vt in request.vehicle_types:
                    if isinstance(vt, VehicleType):
                        vehicle_types.append(vt)
                    elif isinstance(vt, str):
                        try:
                            vehicle_types.append(VehicleType[vt.upper()])
                        except KeyError:
                            raise GetParkingLotRequestValidationException(f"Invalid vehicle type: {vt}")
                    else:
                        raise GetParkingLotRequestValidationException(f"Invalid vehicle type format: {vt}")

            # Step 3: Delegate capacity calculation to the service
            capacity_map = self.parking_lot_service.get_parking_lot_capacity(
                parking_lot_id=request.parking_lot_id,
                parking_floors=request.parking_floor_ids,
                vehicle_types=vehicle_types
            )

            # Step 4: Return success response
            return GetParkingLotCapacityResponseDto(
                response=Response(ResponseStatus.SUCCESS, "Capacity calculated successfully"),
                capacity_map=capacity_map,
            )

        except (InvalidParkingLotException, GetParkingLotRequestValidationException, Exception) as e:
            # Step 5: Catch any errors and return failure response
            error_message = str(e) if str(e) else "Invalid parking lot"
            return GetParkingLotCapacityResponseDto(
                response=Response(ResponseStatus.FAILURE, error_message),
                capacity_map=None,
            )
