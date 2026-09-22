from models import Room
from abc import ABC, abstractmethod
from repositories import RoomRepository
from repositories import UserRepository
from exceptions import UserNotFoundError
from exceptions import UnAuthorizedAccessError
from models import UserType
from models import RoomType
from .room_service import RoomService


class RoomServiceImpl(RoomService):

    def __init__(self, room_repository: RoomRepository, user_repository: UserRepository):
        super().__init__(room_repository, user_repository)

    def add_room(self, user_id: int, room_name: str, description: str, room_type: RoomType, price: float) -> Room:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        if user.user_type != UserType.ADMIN:
            raise UnAuthorizedAccessError("User is not an admin")
        room = Room(room_name=room_name,description=description,price=price,room_type=room_type)
        return self.room_repository.save(room)


