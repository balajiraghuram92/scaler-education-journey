from typing import List
from models.room import Room
from models.room_type import RoomType
from services.room_service import RoomService
from repositories.room_repository import RoomRepository

class RoomServiceImpl(RoomService):
    def __init__(self, room_repo: RoomRepository):
        self.room_repo = room_repo

    def get_rooms(self, room_type_str: str) -> List[Room]:
        if not room_type_str:
            return self.room_repo.get_rooms()
            
        # Parse the string into the RoomType Enum. This will raise a KeyError if invalid.
        mapped_room_type = RoomType[room_type_str.upper()]
        
        return self.room_repo.get_rooms_by_room_type(mapped_room_type)
