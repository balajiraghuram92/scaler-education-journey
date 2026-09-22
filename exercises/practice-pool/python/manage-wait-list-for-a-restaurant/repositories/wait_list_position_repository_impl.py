from datetime import datetime
from typing import Optional, List
from models import WaitListPosition, User
from typing import Dict
from .wait_list_position_repository import WaitListPositionRepository


class InMemoryWaitListPositionRepositoryImpl(WaitListPositionRepository):
    id_Counter = 0

    def __init__(self):
        self._dict: Dict[int, WaitListPosition] = dict()

    def find_by_user(self, user: User) -> Optional[WaitListPosition]:
        for wait_list_position in self._dict.values():
            if wait_list_position.user.id == user.id:
                return wait_list_position
        return None

    def save(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        if wait_list_position.id is None:
            wait_list_position.id = InMemoryWaitListPositionRepositoryImpl.id_Counter + 1
            InMemoryWaitListPositionRepositoryImpl.id_Counter += 1

        self._dict[wait_list_position.id] = wait_list_position
        return wait_list_position

    def delete(self, wait_list_position: WaitListPosition):
        if wait_list_position.id in self._dict:
            self._dict.pop(wait_list_position.id)

    def find_older_than_position(self, wait_list_position: WaitListPosition) -> List[WaitListPosition]:
        filtered = filter(
            lambda position: position.id <= wait_list_position.id,
            self._dict.values()
        )
        return list(filtered)

    def find_all(self):
        return list(sorted(
            self._dict.values(),
            key=lambda position: position.id
        ))

