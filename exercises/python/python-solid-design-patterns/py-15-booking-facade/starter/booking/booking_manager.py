from datetime import date

from .booking_processor import BookingProcessor
from .model import BookingResult
from .services import *


class BookingManager:
    def __init__(
        self,
        availability_service: AvailabilityService,
        payment_service: PaymentService,
        notification_service: NotificationService,
        loyalty_service: LoyaltyService,
        accommodation_details_service: AccommodationDetailsService,
    ):
        self.booking_processor = BookingProcessor(
            availability_service,
            payment_service,
            notification_service,
            loyalty_service,
            accommodation_details_service,
        )

    def book_accommodation(
        self,
        user_id: str,
        accommodation_id: str,
        check_in_date: date,
        check_out_date: date,
    ) -> BookingResult:
        return self.booking_processor.process(
            user_id, accommodation_id, check_in_date, check_out_date
        )
