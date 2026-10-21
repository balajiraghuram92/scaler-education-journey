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
    def __init__(
        self,
        availability_service: AvailabilityService,
        payment_service: PaymentService,
        notification_service: NotificationService,
        loyalty_service: LoyaltyService,
        accommodation_details_service: AccommodationDetailsService,
    ):
        self.availability_service = availability_service
        self.payment_service = payment_service
        self.notification_service = notification_service
        self.loyalty_service = loyalty_service
        self.accommodation_details_service = accommodation_details_service

    def process(
        self,
        user_id: str,
        accommodation_id: str,
        check_in_date: date,
        check_out_date: date,
    ) -> BookingResult:
        is_available = self.availability_service.check_availability(
            accommodation_id, check_in_date, check_out_date
        )
        if not is_available:
            return BookingResult.not_available(
                "Accommodation not available for the given dates"
            )

        payment_status = self.payment_service.make_payment(user_id, accommodation_id)
        # The service may return the Enum member or its name; normalise before comparing.
        if getattr(payment_status, "name", payment_status) != PaymentStatus.SUCCESS.name:
            return BookingResult.payment_failed(
                f"Payment failed with status: {payment_status}"
            )

        confirmation = BookingConfirmation(
            user_id, accommodation_id, check_in_date, check_out_date
        )
        self.notification_service.send_booking_confirmation(confirmation)

        self.loyalty_service.update_loyalty_points(
            user_id, self.payment_service.calculate_payment_amount(accommodation_id)
        )
        self.accommodation_details_service.update_accommodation_details(
            accommodation_id, check_in_date, check_out_date
        )

        return BookingResult.success(confirmation)
