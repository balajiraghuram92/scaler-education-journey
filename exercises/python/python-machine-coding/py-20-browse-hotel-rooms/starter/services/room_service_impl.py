from typing import List
from models.room import Room
from models.room_type import RoomType
from services.room_service import RoomService
from repositories.room_repository import RoomRepository

class RoomServiceImpl(RoomService):

    def __init__(self, room_repo: RoomRepository):
        """Keep the repository."""
        raise NotImplementedError('TODO: implement __init__')

    def get_rooms(self, room_type_str: str) -> List[Room]:
        """None or "" returns every room. Otherwise map the string to RoomType (an invalid string must raise) and return the rooms of that type."""
        raise NotImplementedError('TODO: implement get_rooms')
