from typing import List

from models import Room, RoomType
from repositories import RoomRepository
from services import RoomService


class RoomServiceImpl(RoomService):

    def __init__(self, room_repository: RoomRepository):
        super().__init__(room_repository)

    def get_rooms(self, room_type: str) -> List[Room]:
        if room_type is None:
            return self.room_repository.get_rooms()
        else:
            return self.room_repository.get_rooms_by_room_type(RoomType.__getitem__(room_type))
