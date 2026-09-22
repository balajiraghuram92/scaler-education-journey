from typing import Optional

from .base_model import BaseModel
from .user_type import UserType


class User(BaseModel):
    name: str
    password: str
    phone: str
    user_type: UserType

    def __init__(
            self,
            name: str,
            password: str,
            phone: str,
            user_type: UserType,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.name = name
        self.password = password
        self.phone = phone
        self.user_type = user_type



