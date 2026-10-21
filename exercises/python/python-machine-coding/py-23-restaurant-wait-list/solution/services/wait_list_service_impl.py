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

    def __init__(
        self,
        user_repository: UserRepository,
        wait_list_position_repository: WaitListPositionRepository,
    ):
        self._user_repository = user_repository
        self._wait_list_position_repository = wait_list_position_repository

    def add_user_to_wait_list(self, user_id: int) -> int:
        # Step 1: Check that the user is registered in the system
        user = self._user_repository.find_by_id(user_id)

        # Step 2: If the user doesn't exist, raise our custom exception
        if user is None:
            raise UserNotFoundException("User not found")

        # Step 3: Fetch the current wait list and check if this user is already in it
        current_wait_list = self._wait_list_position_repository.find_all()

        for index, entry in enumerate(current_wait_list):
            if entry.user.id == user_id:
                # User is already in the wait list — return their current position (1-based)
                return index + 1

        # Step 4: User is not in the list yet — create a new entry and save it
        new_entry = WaitListPosition(user=user, inserted_at=datetime.now())
        self._wait_list_position_repository.save(new_entry)

        # Step 5: Their position is the total length of the list after they were added
        return len(self._wait_list_position_repository.find_all())

    def get_wait_list_position(self, user_id: int) -> int:
        # Step 1: Check that the user is registered
        user = self._user_repository.find_by_id(user_id)

        # Step 2: If not found, raise our custom exception
        if user is None:
            raise UserNotFoundException("User not found")

        # Step 3: Search the wait list for this user
        current_wait_list = self._wait_list_position_repository.find_all()

        for index, entry in enumerate(current_wait_list):
            if entry.user.id == user_id:
                # Found — return their 1-based position
                return index + 1

        # Step 4: User is registered but not in the wait list — return -1
        return -1

    def update_wait_list(self, admin_user_id: int, number_of_spots: int) -> None:
        # Step 1: Check that the admin user is registered
        user = self._user_repository.find_by_id(admin_user_id)

        # Step 2: If not found, raise our custom exception
        if user is None:
            raise UserNotFoundException("User not found")

        # Step 3: Check that this user is actually an ADMIN
        if user.user_type != UserType.ADMIN:
            raise UnauthorizedAccessException("Access Denied")

        # Step 4: Determine how many entries to remove.
        # If the requested number is more than the list size, remove all of them.
        current_wait_list = self._wait_list_position_repository.find_all()
        spots_to_remove = min(number_of_spots, len(current_wait_list))

        # Step 5: Remove the first `spots_to_remove` entries from the front of the list
        # We slice the list to get only the entries we need to remove
        for entry in current_wait_list[:spots_to_remove]:
            self._wait_list_position_repository.delete(entry)
