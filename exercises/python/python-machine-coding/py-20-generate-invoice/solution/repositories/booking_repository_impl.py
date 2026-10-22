from typing import List
from models.booking import Booking
from repositories.booking_repository import BookingRepository

class BookingRepositoryImpl(BookingRepository):
    def __init__(self):
        self.bookings = {}
        self.current_id = 1

    def save(self, booking: Booking) -> Booking:
        if booking.id == 0:
            booking.id = self.current_id
            self.current_id += 1
        self.bookings[booking.id] = booking
        return booking

    def find_booking_by_customer_session(self, customer_session_id: int) -> List[Booking]:
        result = []
        for booking in self.bookings.values():
            if booking.customer_session and booking.customer_session.id == customer_session_id:
                result.append(booking)
        return result
