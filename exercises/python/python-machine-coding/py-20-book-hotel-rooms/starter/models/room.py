from models.base_model import BaseModel
from models.room_type import RoomType

class Room(BaseModel):
    def __init__(self):
        super().__init__()
        self.room_number: str = ""
        self.price: float = 0.0
        self.room_type: RoomType = None
        self.description: str = ""
