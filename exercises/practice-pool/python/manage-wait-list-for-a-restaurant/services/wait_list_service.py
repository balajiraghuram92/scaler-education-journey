from abc import ABC, abstractmethod
from typing import List

from models import User


class WaitListService(ABC):

    @abstractmethod
    def add_user_to_wait_list(self, user_id: int) -> int:
        pass

    @abstractmethod
    def get_wait_list_position(self, user_id: int) -> int:
        pass

    @abstractmethod
    def process_wait_list(self, admin_user_id: int, spots_count: int) -> List[User]:
        pass
