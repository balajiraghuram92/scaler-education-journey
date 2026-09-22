from abc import ABC, abstractmethod
from typing import List
from splitwise.models import GroupMember, User, Group


class GroupService(ABC):

    @abstractmethod
    def create_group(
            self,
            user_id: int,
            group_name: str,
            group_description: str
    ) -> Group:
        pass

    @abstractmethod
    def delete_group(
            self,
            admin_id: int,
            group_id: int,
    ):
        pass
