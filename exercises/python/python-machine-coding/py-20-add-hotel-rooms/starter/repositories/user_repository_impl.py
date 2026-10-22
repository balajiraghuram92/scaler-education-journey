from typing import Optional
from models.user import User
from repositories.user_repository import UserRepository

class UserRepositoryImpl(UserRepository):

    def __init__(self):
        """Keep users in a dict keyed by id plus a counter for new ids."""
        raise NotImplementedError('TODO: implement __init__')

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Return the user or None."""
        raise NotImplementedError('TODO: implement find_by_id')

    def save(self, user: User) -> User:
        """Assign the next id when user.id == 0, store the user and return it."""
        raise NotImplementedError('TODO: implement save')
