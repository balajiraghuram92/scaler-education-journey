from datetime import datetime
from services.wait_list_service import WaitListService
from repositories.user_repository import UserRepository
from repositories.wait_list_position_repository import WaitListPositionRepository
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.unauthorized_access_exception import UnauthorizedAccessException
from models.wait_list_position import WaitListPosition
from models.user_type import UserType

class WaitListServiceImpl(WaitListService):
    """
    The concrete implementation of all wait list business logic.

    This class depends on:
      - UserRepository               (to look up registered users)
      - WaitListPositionRepository   (to manage the actual wait list)

    Both are passed in via the constructor — this is Dependency Injection,
    which means we can swap out the implementation of either dependency
    without changing this service at all.
    """

    def __init__(self, user_repository: UserRepository, wait_list_position_repository: WaitListPositionRepository):
        """Keep both repositories."""
        raise NotImplementedError('TODO: implement __init__')

    def add_user_to_wait_list(self, user_id: int) -> int:
        """Unknown user: UserNotFoundException("User not found"). If the user already waits return their 1-based position, otherwise append a WaitListPosition and return the new position."""
        raise NotImplementedError('TODO: implement add_user_to_wait_list')

    def get_wait_list_position(self, user_id: int) -> int:
        """Unknown user: UserNotFoundException("User not found"). The 1-based position, or -1 when the user is not waiting."""
        raise NotImplementedError('TODO: implement get_wait_list_position')

    def update_wait_list(self, admin_user_id: int, number_of_spots: int) -> None:
        """Unknown user: UserNotFoundException("User not found"); non-ADMIN: UnauthorizedAccessException("Access Denied"). Remove min(number_of_spots, length) entries from the front of the list."""
        raise NotImplementedError('TODO: implement update_wait_list')
