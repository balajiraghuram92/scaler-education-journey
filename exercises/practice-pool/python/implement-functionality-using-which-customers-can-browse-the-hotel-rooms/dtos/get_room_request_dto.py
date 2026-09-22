from dataclasses import dataclass, field


@dataclass
class GetRoomsRequestDto:
    room_type: str = field(default=None)
