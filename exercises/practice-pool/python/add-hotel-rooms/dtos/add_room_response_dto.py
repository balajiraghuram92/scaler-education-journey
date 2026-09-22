from dataclasses import dataclass, field
from models import Room
from .response_status import ResponseStatus


@dataclass
class AddRoomResponseDto:
    room: Room = field(default=None)
    response_status: ResponseStatus = field(default=None)
