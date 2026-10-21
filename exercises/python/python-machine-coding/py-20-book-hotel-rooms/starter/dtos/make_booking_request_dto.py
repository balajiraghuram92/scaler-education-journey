from typing import Dict

class MakeBookingRequestDto:
    def __init__(self):
        self.user_id: int = 0
        self.booked_rooms: Dict[int, int] = {}
