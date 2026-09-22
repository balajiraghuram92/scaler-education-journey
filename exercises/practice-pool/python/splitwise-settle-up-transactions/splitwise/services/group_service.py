from abc import ABC, abstractmethod
from typing import List
from splitwise.models import GroupMember, User


class GroupService(ABC):

    @abstractmethod
    def add_member(
            self,
            admin_id: int,
            group_id: int,
            user_id: int
    ) -> GroupMember:
        pass

    @abstractmethod
    def remove_member(
            self,
            admin_id: int,
            group_id: int,
            user_id: int
    ) -> None:
        pass

    @abstractmethod
    def get_members(
            self,
            admin_id: int,
            group_id: int,
    ) -> List[User]:
        pass
