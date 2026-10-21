from models.invoice import Invoice
from models.customer_session_status import CustomerSessionStatus
from exceptions.customer_session_not_found_exception import CustomerSessionNotFoundError
from services.booking_service import BookingService
from repositories.customer_session_repository import CustomerSessionRepository
from repositories.booking_repository import BookingRepository

class BookingServiceImpl(BookingService):
    def __init__(self, session_repo: CustomerSessionRepository, booking_repo: BookingRepository):
        self.session_repo = session_repo
        self.booking_repo = booking_repo

    def generate_invoice(self, user_id: int) -> Invoice:
        session = self.session_repo.find_active_customer_session_by_user_id(user_id)
        if not session:
            raise CustomerSessionNotFoundError("No active customer session found for user.")
        
        bookings = self.booking_repo.find_booking_by_customer_session(session.id)
        
        invoice = Invoice()
        total_price = 0.0
        
        for booking in bookings:
            for room, days in booking.booked_rooms.items():
                if room in invoice.booked_rooms:
                    invoice.booked_rooms[room] += days
                else:
                    invoice.booked_rooms[room] = days
                total_price += room.price * days
                
        invoice.total_amount = total_price
        invoice.gst = total_price * 0.18
        invoice.service_charge = total_price * 0.10
        
        session.customer_session_status = CustomerSessionStatus.ENDED
        self.session_repo.save(session)
        
        return invoice
