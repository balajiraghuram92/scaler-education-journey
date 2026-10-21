from dtos.add_room_request_dto import AddRoomRequestDto
from dtos.add_room_response_dto import AddRoomResponseDto
from dtos.response_status import ResponseStatus
from services.room_service import RoomService

class RoomController:

    def __init__(self, room_service: RoomService):
        """Keep the room service."""
        raise NotImplementedError('TODO: implement __init__')

    def add_room(self, request_dto: AddRoomRequestDto) -> AddRoomResponseDto:
        """Unwrap the request, call the service and return an AddRoomResponseDto: SUCCESS with the room, or FAILURE with room=None when the service raises."""
        raise NotImplementedError('TODO: implement add_room')
