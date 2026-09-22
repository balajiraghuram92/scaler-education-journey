from typing import Optional
from models.room import Room
from .room_repository import RoomRepository
from typing import Dict



class InMemoryRoomRepository(RoomRepository):

    id_Counter = 0

    def __init__(self):
        self._rooms_dict: Dict[int, Room] = dict()

    def find_by_id(self, room_id: int) -> Optional[Room]:
        if room_id not in self._rooms_dict:
            return None
        return self._rooms_dict[room_id]

    def save(self, room: Room) -> Room:
        if room.id is None:
            room.id = InMemoryRoomRepository.id_Counter + 1
            InMemoryRoomRepository.id_Counter += 1
        self._rooms_dict[room.id] = room
        return room
