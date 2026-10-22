from abc import ABC, abstractmethod
from typing import List

from models.wait_list_position import WaitListPosition


class WaitListPositionRepository(ABC):
    @abstractmethod
    def save(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        pass

    @abstractmethod
    def find_all(self) -> List[WaitListPosition]:
        pass

    @abstractmethod
    def delete(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        pass
