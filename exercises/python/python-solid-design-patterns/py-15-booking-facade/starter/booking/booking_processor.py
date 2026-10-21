from datetime import date

from .model import BookingConfirmation, BookingResult, PaymentStatus
from .services import (
    AvailabilityService,
    PaymentService,
    NotificationService,
    LoyaltyService,
    AccommodationDetailsService,
)


class BookingProcessor:
    """Facade that hides the five booking services behind a single call.

    __init__ takes the same five services, in the same order, as BookingManager.__init__
    (availability, payment, notification, loyalty, accommodation details) and stores them.
    """

    def __init__(
        self,
        availability_service: AvailabilityService,
        payment_service: PaymentService,
        notification_service: NotificationService,
        loyalty_service: LoyaltyService,
        accommodation_details_service: AccommodationDetailsService,
    ):
        raise NotImplementedError("Store the five services")

    def process(
        self,
        user_id: str,
        accommodation_id: str,
        check_in_date: date,
        check_out_date: date,
    ) -> BookingResult:
        """Run the booking workflow, in this order:

        1. check_availability(accommodation_id, check_in_date, check_out_date);
           if unavailable return BookingResult.not_available(
           "Accommodation not available for the given dates")
        2. make_payment(user_id, accommodation_id); if the status is not SUCCESS return
           BookingResult.payment_failed(f"Payment failed with status: {status}")
           (the status may arrive as the string "SUCCESS" or as PaymentStatus.SUCCESS)
        3. build a BookingConfirmation and call send_booking_confirmation
        4. update_loyalty_points(user_id, calculate_payment_amount(accommodation_id))
        5. update_accommodation_details(accommodation_id, check_in_date, check_out_date)
        6. return BookingResult.success(confirmation)
        """
        raise NotImplementedError("Implement the booking workflow")
