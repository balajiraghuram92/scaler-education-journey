from models import Room
from abc import ABC, abstractmethod
from repositories import RoomRepository
from repositories import UserRepository


class RoomService(ABC):

    def __init__(self, room_repository: RoomRepository, user_repository: UserRepository):
        self.room_repository = room_repository
        self.user_repository = user_repository

    @abstractmethod
    def add_room(self, user_id: int, room_name: str, price: float, room_type: str, description: str) -> Room:
        pass