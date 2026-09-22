from dataclasses import dataclass, field


@dataclass
class AddRoomRequestDto:
    user_id: int
    room_name: str
    price: float
    room_type: str
    description: str
