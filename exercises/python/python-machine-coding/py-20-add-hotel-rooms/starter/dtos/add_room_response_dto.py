from typing import Optional
from models.room import Room
from dtos.response_status import ResponseStatus

class AddRoomResponseDto:
    def __init__(self):
        self.room: Optional[Room] = None
        self.response_status: ResponseStatus = None
