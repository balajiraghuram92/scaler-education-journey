from abc import ABC, abstractmethod
from typing import Optional
from models.room import Room

class RoomRepository(ABC):
    @abstractmethod
    def save(self, room: Room) -> Room:
        pass

    @abstractmethod
    def find_by_id(self, room_id: int) -> Optional[Room]:
        pass
