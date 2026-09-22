from .booking_repository import BookingRepository
from typing import Dict, List

from models import Booking


class InMemoryBookingRepository(BookingRepository):
    id_Counter = 0

    def __init__(self):
        self._booking_dict: Dict[int, Booking] = dict()

    def save(self, booking: Booking) -> Booking:
        if booking.id is None:
            booking.id = InMemoryBookingRepository.id_Counter + 1
            InMemoryBookingRepository.id_Counter += 1

        self._booking_dict[booking.id] = booking
        return booking

    def find_bookings_by_customer_session(self, session_id):

        filtered = filter(
            lambda booking: booking.customer_session.id == session_id,
            self._booking_dict.values()
        )

        return list(filtered)




