from typing import List
from models import Booking
from models import CustomerSession
from models import CustomerSessionStatus
from models import Invoice
from repositories.customer_session_repository import CustomerSessionRepository
from repositories.booking_repository import BookingRepository
from exceptions.customer_session_not_found_error import CustomerSessionNotFoundException
from .booking_service import BookingService


class BookingServiceImpl(BookingService):

    def __init__(
            self,
            customer_session_repository: CustomerSessionRepository,
            booking_repository: BookingRepository
    ):
        super().__init__(
            customer_session_repository,
            booking_repository
        )

    def generate_invoice(self, user_id: int) -> Invoice:
        customer_session: CustomerSession = self.customer_session_repository.find_active_customer_session_by_user_id(user_id)
        if customer_session is None:
            raise CustomerSessionNotFoundException("Customer session not found")

        bookings: List[Booking] = self.booking_repository.find_bookings_by_customer_session(customer_session.id)

        booked_rooms = []
        total_invoice_amount = 0.0

        for booking in bookings:
            for room, days in booking.booked_rooms:
                booked_rooms.append([room, days])
                total_invoice_amount += (room.price * days)

        service_charge = total_invoice_amount * 0.1
        gst = total_invoice_amount * 0.18

        total_invoice_amount += (service_charge + gst)

        customer_session.customer_session_status = CustomerSessionStatus.ENDED
        self.customer_session_repository.save(customer_session)

        invoice = Invoice(
            booked_rooms=booked_rooms,
            gst=gst,
            service_charge=service_charge,
            total_amount=total_invoice_amount
        )

        return invoice










