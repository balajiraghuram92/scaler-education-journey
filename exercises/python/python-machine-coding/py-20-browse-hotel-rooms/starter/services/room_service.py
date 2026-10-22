from abc import ABC, abstractmethod
from typing import List
from models.room import Room

class RoomService(ABC):
    @abstractmethod
    def get_rooms(self, room_type: str) -> List[Room]:
        pass
