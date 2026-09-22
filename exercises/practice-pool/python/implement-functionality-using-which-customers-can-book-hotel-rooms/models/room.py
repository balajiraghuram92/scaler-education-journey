from typing import Optional

from .base_model import BaseModel
from .room_type import RoomType


class Room(BaseModel):
    room_name: str
    price: float
    room_type: RoomType
    description: str

    def __init__(
            self,
            room_name: str,
            price: float,
            room_type: RoomType,
            description: str,
            id: Optional[id] = None
    ):
        super().__init__(id)
        self.room_name = room_name
        self.price = price
        self.room_type = room_type
        self.description = description
