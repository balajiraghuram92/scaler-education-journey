from typing import List
from models.room import Room
from models.room_type import RoomType
from repositories.room_repository import RoomRepository

class RoomRepositoryImpl(RoomRepository):

    def __init__(self):
        """Keep rooms in a dict keyed by id plus a counter that hands out ids 1, 2, 3..."""
        raise NotImplementedError('TODO: implement __init__')

    def add(self, room: Room) -> Room:
        """Same as save."""
        raise NotImplementedError('TODO: implement add')

    def get_rooms(self) -> List[Room]:
        """All stored rooms, in insertion order."""
        raise NotImplementedError('TODO: implement get_rooms')

    def get_rooms_by_room_type(self, room_type: RoomType) -> List[Room]:
        """Only the rooms whose room_type equals the given RoomType."""
        raise NotImplementedError('TODO: implement get_rooms_by_room_type')

    def save(self, room: Room) -> Room:
        """Assign the next id when room.id == 0, store the room and return it."""
        raise NotImplementedError('TODO: implement save')
