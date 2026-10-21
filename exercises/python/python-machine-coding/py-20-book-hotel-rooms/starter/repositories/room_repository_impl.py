from typing import Optional
from models.room import Room
from repositories.room_repository import RoomRepository

class RoomRepositoryImpl(RoomRepository):
    def __init__(self):
        self.rooms = {}
        self.current_id = 1

    def save(self, room: Room) -> Room:
        if room.id == 0:
            room.id = self.current_id
            self.current_id += 1
        self.rooms[room.id] = room
        return room

    def find_by_id(self, room_id: int) -> Optional[Room]:
        return self.rooms.get(room_id)
