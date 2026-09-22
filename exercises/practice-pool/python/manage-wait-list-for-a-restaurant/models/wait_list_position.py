from typing import Optional

from .base_model import BaseModel
from .user import User
from datetime import datetime


class WaitListPosition(BaseModel):
    user: User
    inserted_at: datetime

    def __init__(
            self,
            user: User,
            inserted_at: datetime = datetime.now(),
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.user = user
        self.inserted_at = inserted_at
