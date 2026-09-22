from typing import Optional
from models import User


class UserRepository:
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    def save(self, user: User) -> User:
        pass