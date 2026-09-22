from typing import Optional
from models.room import Room
from abc import ABC, abstractmethod


class RoomRepository(ABC):

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Room]:
        pass

    @abstractmethod
    def save(self, room: Room) -> Room:
        pass
