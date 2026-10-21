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
        """Keep both repositories."""
        raise NotImplementedError('TODO: implement __init__')

    def add_room(self, user_id: int, room_name: str, price: float, room_type_str: str, description: str) -> Room:
        """Validate in order: user exists (UserNotFoundError), user is ADMIN (UnauthorizedAccessError), room type string maps to RoomType (ValueError). Only then build a Room, save it and return it."""
        raise NotImplementedError('TODO: implement add_room')
