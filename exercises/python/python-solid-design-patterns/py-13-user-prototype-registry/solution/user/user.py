from __future__ import annotations

from copy import deepcopy
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
        return deepcopy(self)
