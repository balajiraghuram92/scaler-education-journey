from typing import Optional
from models.user import User
from repositories.user_repository import UserRepository

class UserRepositoryImpl(UserRepository):
    def __init__(self):
        self.users = {}
        self.current_id = 1

    def save(self, user: User) -> User:
        if user.id == 0:
            user.id = self.current_id
            self.current_id += 1
        self.users[user.id] = user
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)
