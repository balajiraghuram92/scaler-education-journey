from models.booking import Booking
from repositories.booking_repository import BookingRepository

class BookingRepositoryImpl(BookingRepository):

    def __init__(self):
        raise NotImplementedError('TODO: implement __init__')

    def save(self, booking: Booking) -> Booking:
        """Assign the next id when booking.id == 0, store the booking and return it."""
        raise NotImplementedError('TODO: implement save')
