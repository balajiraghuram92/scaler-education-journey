from models.invoice import Invoice
from models.customer_session_status import CustomerSessionStatus
from exceptions.customer_session_not_found_exception import CustomerSessionNotFoundError
from services.booking_service import BookingService
from repositories.customer_session_repository import CustomerSessionRepository
from repositories.booking_repository import BookingRepository

class BookingServiceImpl(BookingService):

    def __init__(self, session_repo: CustomerSessionRepository, booking_repo: BookingRepository):
        raise NotImplementedError('TODO: implement __init__')

    def generate_invoice(self, user_id: int) -> Invoice:
        """Find the ACTIVE session for the user (CustomerSessionNotFoundError if none), merge booked_rooms of all its bookings (summing days per room), set total_amount = sum(price x days), gst = 18% and service_charge = 10% of the total. Mark the session ENDED, save it and return the Invoice."""
        raise NotImplementedError('TODO: implement generate_invoice')
