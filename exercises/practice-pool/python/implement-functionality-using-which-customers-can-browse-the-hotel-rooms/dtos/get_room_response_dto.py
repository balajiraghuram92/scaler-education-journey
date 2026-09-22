from .response_status import ResponseStatus
from models import Room
from typing import List
from dataclasses import dataclass, field


@dataclass
class GetRoomsResponseDto:
    response_status: ResponseStatus = field(default=None)
    rooms: List[Room] = field(default_factory=list)
