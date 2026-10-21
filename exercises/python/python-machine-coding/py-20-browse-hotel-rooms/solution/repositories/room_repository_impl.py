from typing import List
from models.room import Room
from models.room_type import RoomType
from repositories.room_repository import RoomRepository

class RoomRepositoryImpl(RoomRepository):
    def __init__(self):
        self.rooms = {}
        self.current_id = 1

    def add(self, room: Room) -> Room:
        return self.save(room)

    def get_rooms(self) -> List[Room]:
        return list(self.rooms.values())

    def get_rooms_by_room_type(self, room_type: RoomType) -> List[Room]:
        return [room for room in self.rooms.values() if room.room_type == room_type]

    def save(self, room: Room) -> Room:
        if room.id == 0:
            room.id = self.current_id
            self.current_id += 1
        self.rooms[room.id] = room
        return room
