from services import RoomService
from dtos import GetRoomsRequestDto
from dtos import GetRoomsResponseDto
from dtos import ResponseStatus
from traceback import print_exc


class RoomController:
    def __init__(self, room_service: RoomService):
        self.room_service = room_service

    def get_rooms(self, request_dto: GetRoomsRequestDto) -> GetRoomsResponseDto:
        response_dto = GetRoomsResponseDto()
        try:
            rooms = self.room_service.get_rooms(request_dto.room_type)
            response_dto.response_status = ResponseStatus.SUCCESS
            response_dto.rooms = rooms
            return response_dto

        except Exception as e:
            print_exc()
            response_dto.response_status = ResponseStatus.FAILURE
            return response_dto

