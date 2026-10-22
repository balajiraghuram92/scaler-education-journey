from typing import Dict, Optional

from .user import User, UserType
from .registry import UserPrototypeRegistry


class UserPrototypeRegistryImpl(UserPrototypeRegistry):
    """Keeps one prototype user per UserType and hands out clones."""

    def __init__(self):
        self.prototypes: Dict[UserType, User] = {}

    def add_prototype(self, user: User) -> None:
        """Store the user keyed by its ``type_`` (a second one of the same type replaces it)."""
        raise NotImplementedError("Implement add_prototype")

    def get_prototype(self, type_: UserType) -> Optional[User]:
        """Return the stored prototype itself, or None if there is none."""
        raise NotImplementedError("Implement get_prototype")

    def clone(self, type_: UserType) -> Optional[User]:
        """Return a CLONE of the stored prototype, or None for an unknown type."""
        raise NotImplementedError("Implement clone")
