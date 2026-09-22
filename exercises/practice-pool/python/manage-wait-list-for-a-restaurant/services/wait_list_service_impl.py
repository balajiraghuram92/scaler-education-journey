from typing import List

from .wait_list_service import WaitListService
from repositories import WaitListPositionRepository
from repositories import UserRepository
from models import User, WaitListPosition, UserType
from exceptions import UnauthorizedAccessError, UserNotFoundError, UserNotOnListError
from datetime import datetime


class WaitListServiceImpl(WaitListService):
    wait_list_position_repository: WaitListPositionRepository
    user_repository: UserRepository

    def __init__(
            self,
            wait_list_position_repository: WaitListPositionRepository,
            user_repository: UserRepository
    ):
        self.user_repository = user_repository
        self.wait_list_position_repository = wait_list_position_repository

    def add_user_to_wait_list(self, user_id: int) -> int:
        user: User = self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError("No user with user_id: {}".format(user_id))

        wait_list_position = self.wait_list_position_repository.find_by_user(user)

        if wait_list_position is None:
            wait_list_position = WaitListPosition(
                user=user,
                inserted_at=datetime.now()
            )

            self.wait_list_position_repository.save(wait_list_position)

        return self.get_wait_list_position(user_id)

    def get_wait_list_position(self, user_id: int) -> int:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError("No user with user_id: {}".format(user_id))
        wait_list_position = self.wait_list_position_repository.find_by_user(user)
        if wait_list_position is None:
            raise UserNotOnListError("No user with user_id: {} is on the list".format(user_id))
        positions = self.wait_list_position_repository.find_older_than_position(wait_list_position)
        return len(positions)

    def process_wait_list(self, admin_user_id: int, spots_count: int) -> List[User]:
        admin_user = self.user_repository.find_by_id(admin_user_id)
        if admin_user is None:
            raise UserNotFoundError("No user with user_id: {}".format(admin_user_id))
        if admin_user.user_type != UserType.ADMIN:
            raise UnauthorizedAccessError("User with user_id: {} does not have access".format(admin_user_id))

        positions: List[WaitListPosition] = self.wait_list_position_repository.find_all()
        spots_count = min(len(positions), spots_count)
        users = []

        for i in range(spots_count):
            self.wait_list_position_repository.delete(positions[i])
            users.append(positions[i].user)

        return users

