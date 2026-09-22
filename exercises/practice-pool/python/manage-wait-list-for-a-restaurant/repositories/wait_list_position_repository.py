from typing import List, Optional
from models import WaitListPosition, User
from abc import ABC, abstractmethod
from datetime import datetime


class WaitListPositionRepository(ABC):
    @abstractmethod
    def find_older_than_position(self, wait_list_position: WaitListPosition) -> List[WaitListPosition]:
        pass

    @abstractmethod
    def find_by_user(self, user: User) -> Optional[WaitListPosition]:
        pass

    @abstractmethod
    def save(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        pass

    @abstractmethod
    def delete(self, wait_list_position: WaitListPosition):
        pass

    @abstractmethod
    def find_all(self):
        pass
