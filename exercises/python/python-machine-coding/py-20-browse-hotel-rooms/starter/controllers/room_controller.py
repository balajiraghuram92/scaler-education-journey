from dtos.get_rooms_request_dto import GetRoomsRequestDto
from dtos.get_rooms_response_dto import GetRoomsResponseDto
from dtos.response_status import ResponseStatus
from services.room_service import RoomService

class RoomController:

    def __init__(self, room_service: RoomService):
        """Keep the room service."""
        raise NotImplementedError('TODO: implement __init__')

    def get_rooms(self, request_dto: GetRoomsRequestDto) -> GetRoomsResponseDto:
        """Return a GetRoomsResponseDto: SUCCESS with the rooms, or FAILURE with an empty list when the service raises."""
        raise NotImplementedError('TODO: implement get_rooms')
