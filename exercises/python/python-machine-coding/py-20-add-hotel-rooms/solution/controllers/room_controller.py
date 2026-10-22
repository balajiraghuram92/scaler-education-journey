from dtos.add_room_request_dto import AddRoomRequestDto
from dtos.add_room_response_dto import AddRoomResponseDto
from dtos.response_status import ResponseStatus
from services.room_service import RoomService

class RoomController:
    def __init__(self, room_service: RoomService):
        self.room_service = room_service

    def add_room(self, request_dto: AddRoomRequestDto) -> AddRoomResponseDto:
        response = AddRoomResponseDto()
        try:
            room = self.room_service.add_room(
                request_dto.user_id,
                request_dto.name,
                request_dto.price,
                request_dto.room_type,
                request_dto.description
            )
            response.room = room
            response.response_status = ResponseStatus.SUCCESS
        except Exception:
            response.response_status = ResponseStatus.FAILURE
            
        return response
