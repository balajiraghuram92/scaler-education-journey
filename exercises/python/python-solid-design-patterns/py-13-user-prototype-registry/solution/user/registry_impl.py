from typing import Dict, Optional

from .user import User, UserType
from .registry import UserPrototypeRegistry


class UserPrototypeRegistryImpl(UserPrototypeRegistry):
    def __init__(self):
        self.prototypes: Dict[UserType, User] = {}

    def add_prototype(self, user: User) -> None:
        self.prototypes[user.type_] = user

    def get_prototype(self, type_: UserType) -> Optional[User]:
        return self.prototypes.get(type_)

    def clone(self, type_: UserType) -> Optional[User]:
        return (
            self.prototypes[type_].clone_object() if type_ in self.prototypes else None
        )
