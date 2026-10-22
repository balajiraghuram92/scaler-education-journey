from models.room import Room
from models.room_type import RoomType
from models.user_type import UserType
from exceptions.user_not_found_exception import UserNotFoundError
from exceptions.unauthorized_access import UnauthorizedAccessError
from services.room_service import RoomService
from repositories.user_repository import UserRepository
from repositories.room_repository import RoomRepository

class RoomServiceImpl(RoomService):
    def __init__(self, user_repo: UserRepository, room_repo: RoomRepository):
        self.user_repo = user_repo
        self.room_repo = room_repo

    def add_room(self, user_id: int, room_name: str, price: float, room_type_str: str, description: str) -> Room:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found.")

        if user.user_type != UserType.ADMIN:
            raise UnauthorizedAccessError("Only ADMIN users can add a room.")

        # Map string to RoomType enum
        try:
            mapped_room_type = RoomType[room_type_str.upper()]
        except KeyError:
            # If the user provides an invalid type, we can map it to None or raise an error.
            # But according to requirements, we just proceed.
            raise ValueError(f"Invalid room type: {room_type_str}")

        room = Room()
        room.name = room_name
        room.price = price
        room.room_type = mapped_room_type
        room.description = description

        saved_room = self.room_repo.save(room)
        return saved_room
