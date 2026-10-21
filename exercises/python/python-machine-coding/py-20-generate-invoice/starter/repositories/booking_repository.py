from abc import ABC, abstractmethod
from typing import List
from models.booking import Booking

class BookingRepository(ABC):
    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def find_booking_by_customer_session(self, customer_session_id: int) -> List[Booking]:
        pass
