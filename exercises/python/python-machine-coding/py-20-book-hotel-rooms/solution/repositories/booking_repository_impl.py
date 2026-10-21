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
