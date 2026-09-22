from typing import List
from models import Room, RoomType
from abc import ABC, abstractmethod


class RoomRepository(ABC):

    @abstractmethod
    def add(self, room: Room) -> Room:
        pass

    @abstractmethod
    def get_rooms(self) -> List[Room]:
        pass

    @abstractmethod
    def get_rooms_by_room_type(self, room_type: RoomType) -> List[Room]:
        pass

    @abstractmethod
    def save(self, room: Room) -> Room:
        pass
