from typing import Optional
from repositories.user_repository import UserRepository
from models.user import User


class UserRepositoryImpl(UserRepository):
    """
    The in-memory implementation of UserRepository.

    We store all users in a Python dictionary where:
      key   = the user's ID (an integer)
      value = the User object itself

    A counter (_current_id) starts at 1 and increases by 1 every time
    a new user is saved, giving each user a unique ID automatically.
    """

    def __init__(self):
        # Our in-memory "database" — maps user ID → User object
        self._users: dict = {}
        # Auto-increment counter for assigning IDs
        self._current_id: int = 1

    def save(self, user: User) -> User:
        # Assign the next available ID to this user
        user.id = self._current_id
        # Store in the dictionary
        self._users[user.id] = user
        # Increment so the next user gets a different ID
        self._current_id += 1
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        # dict.get() returns None automatically if the key doesn't exist
        return self._users.get(user_id)
