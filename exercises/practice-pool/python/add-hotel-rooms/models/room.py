from .base_model import BaseModel
from .room_type import RoomType


class Room(BaseModel):
    room_name: str
    price: float
    room_type: RoomType
    description: str

    def __init__(self, room_name=None, price=0.0, room_type=None, description=''):
        super().__init__()
        self.room_name = room_name
        self.price = price
        self.room_type = room_type
        self.description = description
