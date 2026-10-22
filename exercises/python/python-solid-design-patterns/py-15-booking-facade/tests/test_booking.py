from datetime import date

from booking.booking_manager import BookingManager
from booking.booking_processor import BookingProcessor
from booking.model import BookingConfirmation, BookingStatus, PaymentStatus
from booking.services import (
    AccommodationDetailsService,
    AvailabilityService,
    LoyaltyService,
    NotificationService,
    PaymentService,
)

CHECK_IN, CHECK_OUT = date(2025, 8, 1), date(2025, 8, 5)


class Log:
    def __init__(self):
        self.events = []

    def names(self):
        return [e[0] for e in self.events]


class FakeAvailability:
    def __init__(self, log, available=True):
        self.log, self.available = log, available

    def check_availability(self, accommodation_id, check_in, check_out):
        self.log.events.append(("availability", accommodation_id, check_in, check_out))
        return self.available


class FakePayment:
    def __init__(self, log, status="SUCCESS", amount=120.0):
        self.log, self.status, self.amount = log, status, amount

    def make_payment(self, user_id, accommodation_id):
        self.log.events.append(("payment", user_id, accommodation_id))
        return self.status

    def calculate_payment_amount(self, accommodation_id):
        self.log.events.append(("amount", accommodation_id))
        return self.amount


class FakeNotification:
    def __init__(self, log):
        self.log = log

    def send_booking_confirmation(self, confirmation):
        self.log.events.append(("notify", confirmation))


class FakeLoyalty:
    def __init__(self, log):
        self.log = log

    def update_loyalty_points(self, user_id, amount):
        self.log.events.append(("loyalty", user_id, amount))


class FakeDetails:
    def __init__(self, log):
        self.log = log

    def update_accommodation_details(self, accommodation_id, check_in, check_out):
        self.log.events.append(("details", accommodation_id, check_in, check_out))


def processor(log, available=True, status="SUCCESS"):
    return BookingProcessor(
        FakeAvailability(log, available),
        FakePayment(log, status),
        FakeNotification(log),
        FakeLoyalty(log),
        FakeDetails(log),
    )


def test_manager_does_not_keep_the_services():
    manager = BookingManager(
        AvailabilityService(), PaymentService(), NotificationService(),
        LoyaltyService(), AccommodationDetailsService(),
    )
    for name in ("availability_service", "payment_service", "notification_service",
                 "loyalty_service", "accommodation_details_service"):
        assert not hasattr(manager, name), f"BookingManager must not expose {name}; only the facade should know it"


def test_processor_takes_services_in_the_managers_order():
    log = Log()
    proc = processor(log)
    result = proc.process("u1", "acc9", CHECK_IN, CHECK_OUT)
    assert result.status is BookingStatus.SUCCESS, "positional order must be availability, payment, notification, loyalty, details"


def test_happy_path_calls_every_step_in_order():
    log = Log()
    processor(log).process("u1", "acc9", CHECK_IN, CHECK_OUT)
    steps = [n for n in log.names() if n != "amount"]
    assert steps == ["availability", "payment", "notify", "loyalty", "details"], f"wrong workflow order: {steps}"


def test_each_step_receives_the_exact_arguments():
    log = Log()
    result = processor(log).process("u1", "acc9", CHECK_IN, CHECK_OUT)
    ev = {e[0]: e for e in log.events}
    assert ev["availability"] == ("availability", "acc9", CHECK_IN, CHECK_OUT)
    assert ev["payment"] == ("payment", "u1", "acc9")
    assert ev["loyalty"] == ("loyalty", "u1", 120.0), "loyalty points must use calculate_payment_amount(accommodation_id)"
    assert ev["details"] == ("details", "acc9", CHECK_IN, CHECK_OUT)
    assert ev["notify"][1] == BookingConfirmation("u1", "acc9", CHECK_IN, CHECK_OUT)
    assert result.confirmation is ev["notify"][1], "the notified confirmation is the one returned in the result"


def test_unavailable_stops_before_payment():
    log = Log()
    result = processor(log, available=False).process("u1", "acc9", CHECK_IN, CHECK_OUT)
    assert result.status is BookingStatus.NOT_AVAILABLE
    assert result.error_message == "Accommodation not available for the given dates"
    assert log.names() == ["availability"], f"nothing after the availability check may run, ran {log.names()}"


def test_payment_failure_stops_before_side_effects():
    log = Log()
    result = processor(log, status="DECLINED").process("u1", "acc9", CHECK_IN, CHECK_OUT)
    assert result.status is BookingStatus.PAYMENT_FAILED
    assert result.error_message == "Payment failed with status: DECLINED"
    assert result.confirmation is None
    assert log.names() == ["availability", "payment"], f"no notification, loyalty or details update after a failed payment, ran {log.names()}"


def test_payment_status_may_be_a_string_or_an_enum():
    ok = processor(Log(), status=PaymentStatus.SUCCESS).process("u", "a", CHECK_IN, CHECK_OUT)
    assert ok.status is BookingStatus.SUCCESS, "PaymentStatus.SUCCESS (what the real service returns) must count as success"
    bad = processor(Log(), status=PaymentStatus.FAILED).process("u", "a", CHECK_IN, CHECK_OUT)
    assert bad.status is BookingStatus.PAYMENT_FAILED, "PaymentStatus.FAILED must count as a failed payment"


def test_manager_delegates_to_the_facade_with_real_services():
    manager = BookingManager(
        AvailabilityService(), PaymentService(), NotificationService(),
        LoyaltyService(), AccommodationDetailsService(),
    )
    result = manager.book_accommodation("123", "456", CHECK_IN, CHECK_OUT)
    assert result.status is BookingStatus.SUCCESS
    assert result.confirmation == BookingConfirmation("123", "456", CHECK_IN, CHECK_OUT)
