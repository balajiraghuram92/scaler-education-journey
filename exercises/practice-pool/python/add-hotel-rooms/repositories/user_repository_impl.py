from typing import Optional
from models import User
from typing import Dict
from .user_repository import UserRepository


class InMemoryUserRepositoryImpl(UserRepository):
    id_Counter = 0

    def __init__(self):
        self._users_dict: Dict[int, User] = dict()

    def find_by_id(self, user_id: int) -> Optional[User]:
        if user_id in self._users_dict:
            return self._users_dict[user_id]
        else:
            return None

    def save(self, user: User) -> User:
        if user.id in self._users_dict:
            self._users_dict[user.id] = user
            return user
        else:
            user.id = InMemoryUserRepositoryImpl.id_Counter + 1
            InMemoryUserRepositoryImpl.id_Counter += 1
            self._users_dict[user.id] = user
            return user
