from abc import ABC, abstractmethod
from typing import Dict
from models.booking import Booking

class BookingService(ABC):
    @abstractmethod
    def make_booking(self, user_id: int, rooms_to_be_booked: Dict[int, int]) -> Booking:
        pass
