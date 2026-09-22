from typing import List
from models.room import Room
from repositories import RoomRepository
from abc import ABC, abstractmethod


class RoomService(ABC):

    def __init__(self, room_repository: RoomRepository):
        self.room_repository = room_repository

    @abstractmethod
    def get_rooms(self, room_type: str) -> List[Room]:
        pass

