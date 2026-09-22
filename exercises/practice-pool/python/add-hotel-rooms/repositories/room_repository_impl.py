from typing import List
from models import Room
from models import RoomType
from .room_repository import RoomRepository
from typing import Dict


class InMemoryRoomRepository(RoomRepository):

    id_Counter = 0

    def __init__(self):
        self._rooms_dict: Dict[int, Room] = dict()

    def add(self, room: Room) -> Room:
        if room.id == 0:
            room.id = InMemoryRoomRepository.id_Counter + 1
            InMemoryRoomRepository.id_Counter += 1
        self._rooms_dict[room.id] = room
        return room

    def get_rooms(self) -> List[Room]:
        return list(self._rooms_dict.values())

    def get_rooms_by_room_type(self, room_type: RoomType) -> List[Room]:
        filtered = filter(lambda room: room.room_type == room_type, self._rooms_dict.values())
        return list(filtered)

    def save(self, room: Room) -> Room:
        if room.id == 0:
            room.id = InMemoryRoomRepository.id_Counter + 1
            InMemoryRoomRepository.id_Counter += 1
        self._rooms_dict[room.id] = room
        return room
