from typing import Dict, Optional
from models.user import User
from repositories.user_repository import UserRepository

class UserRepositoryImpl(UserRepository):
    def __init__(self):
        self._store: Dict[int, User] = {}
        self._next_id = 1

    def save(self, user: User) -> User:
        if user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user
        return user

    def find_user_by_id(self, user_id: int) -> Optional[User]:
        return self._store.get(user_id)
