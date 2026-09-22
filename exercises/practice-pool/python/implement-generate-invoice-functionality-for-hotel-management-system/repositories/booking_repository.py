from abc import ABC, abstractmethod
from typing import List

from models import Booking


class BookingRepository(ABC):

    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def find_bookings_by_customer_session(self, session_id: int) -> List[Booking]:
        pass
