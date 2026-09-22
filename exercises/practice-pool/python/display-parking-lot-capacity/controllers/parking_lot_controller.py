from services.parking_lot_service import ParkingLotService
from dtos import GetParkingLotCapacityRequestDto, GetParkingLotCapacityResponseDto
from dtos import ResponseStatus


class ParkingLotController:
    parking_lot_service: ParkingLotService

    def __init__(self, parking_lot_service: ParkingLotService):
        self.parking_lot_service = parking_lot_service

    def get_capacity(self, request_dto: GetParkingLotCapacityRequestDto):
        try:
            capacity = self.parking_lot_service.get_parking_lot_capacity(
                parking_lot_id=request_dto.parking_lot_id,
                parking_floor_ids=request_dto.parking_floor_ids,
                vehicle_types=request_dto.vehicle_types
            )

            return GetParkingLotCapacityResponseDto(
                response_status=ResponseStatus.SUCCESS,
                capacity=capacity
            )
        except Exception as e:
            return GetParkingLotCapacityResponseDto(
                response_status=ResponseStatus.FAILURE,
                capacity=None
            )
