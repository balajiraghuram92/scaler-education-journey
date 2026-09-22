from services import RoomService
from dtos import AddRoomRequestDto
from dtos import AddRoomResponseDto
from dtos import ResponseStatus


class RoomController():
    def __init__(self, room_service: RoomService):
        self.room_service = room_service

    def add_room(self, request_dto: AddRoomRequestDto) -> AddRoomResponseDto:
        response_dto: AddRoomResponseDto = AddRoomResponseDto()

        try:
            room = self.room_service.add_room(
                user_id=request_dto.user_id,
                room_name=request_dto.room_name,
                description=request_dto.description,
                room_type=request_dto.room_type,
                price=request_dto.price
            )

            if room is None:
                response_dto.response_status = ResponseStatus.FAILURE
                response_dto.room = None
            else:
                response_dto.response_status = ResponseStatus.SUCCESS
                response_dto.room = room

        except Exception:
            response_dto.response_status = ResponseStatus.FAILURE
            response_dto.room = None

        return response_dto
