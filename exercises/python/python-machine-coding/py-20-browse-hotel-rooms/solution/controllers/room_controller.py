from dtos.get_rooms_request_dto import GetRoomsRequestDto
from dtos.get_rooms_response_dto import GetRoomsResponseDto
from dtos.response_status import ResponseStatus
from services.room_service import RoomService

class RoomController:
    def __init__(self, room_service: RoomService):
        self.room_service = room_service

    def get_rooms(self, request_dto: GetRoomsRequestDto) -> GetRoomsResponseDto:
        response = GetRoomsResponseDto()
        try:
            rooms = self.room_service.get_rooms(request_dto.room_type)
            response.rooms = rooms
            response.response_status = ResponseStatus.SUCCESS
        except Exception:
            response.rooms = []
            response.response_status = ResponseStatus.FAILURE
            
        return response
