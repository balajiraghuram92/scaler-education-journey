from dataclasses import dataclass
from typing import List


@dataclass
class MakeBookingRequestDto:
    user_id: int
    rooms_to_be_booked: List[List[int]]  # List of [room_id, days]
