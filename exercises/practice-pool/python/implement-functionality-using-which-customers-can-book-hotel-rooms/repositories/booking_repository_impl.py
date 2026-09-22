from .booking_repository import BookingRepository
from typing import Dict

from models.booking import Booking


class InMemoryBookingRepository(BookingRepository):
    id_Counter = 0

    def __init__(self):
        self._rooms_dict: Dict[int, Booking] = dict()

    def save(self, booking: Booking) -> Booking:
        if booking.id is None:
            booking.id = InMemoryBookingRepository.id_Counter + 1
            InMemoryBookingRepository.id_Counter += 1

        self._rooms_dict[booking.id] = booking
        return booking



