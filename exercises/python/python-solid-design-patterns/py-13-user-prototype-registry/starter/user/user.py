from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cloneable import Cloneable


class UserType(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ADMIN = "admin"


@dataclass
class User(Cloneable):
    user_id: int
    username: str
    email: str
    display_name: str
    age: int
    type_: UserType

    def clone_object(self) -> User:
        """Return an independent copy of this user (the Prototype operation).

        Changing the copy must never change the original.
        """
        raise NotImplementedError("Implement clone_object")
