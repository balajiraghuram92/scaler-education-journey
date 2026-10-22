from typing import List
from models.room import Room
from dtos.response_status import ResponseStatus

class GetRoomsResponseDto:
    def __init__(self):
        self.response_status: ResponseStatus = None
        self.rooms: List[Room] = []
