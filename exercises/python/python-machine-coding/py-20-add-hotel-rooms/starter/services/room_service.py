from abc import ABC, abstractmethod
from models.room import Room

class RoomService(ABC):
    @abstractmethod
    def add_room(self, user_id: int, room_name: str, price: float, room_type: str, description: str) -> Room:
        pass
