from datetime import date, datetime

import pytest

from parking.billing import Bill, OverpaymentError, Payment, PaymentService, PaymentStatus, Spot, SpotStatus
from parking.fees import (
    FeeStrategy,
    FeeStrategyFactory,
    HolidayFee,
    Slab,
    VehicleType,
    WeekdayFee,
    WeekendSlabFee,
    started_hours,
)

CAR_SLABS = [Slab(0, 2, 20), Slab(2, 4, 30), Slab(4, 6, 40), Slab(6, -1, 50)]


def weekend_fee():
    return WeekendSlabFee({VehicleType.CAR: CAR_SLABS})


def test_started_hours_rounds_up_with_a_one_hour_minimum():
    t = datetime(2026, 1, 5, 10, 0)
    assert started_hours(t, t) == 1, "minimum is one hour"
    assert started_hours(t, datetime(2026, 1, 5, 10, 1)) == 1
    assert started_hours(t, datetime(2026, 1, 5, 11, 0)) == 1
    assert started_hours(t, datetime(2026, 1, 5, 11, 1)) == 2
    assert started_hours(t, datetime(2026, 1, 6, 10, 0)) == 24


@pytest.mark.parametrize("vehicle_type", list(VehicleType))
def test_weekday_rounds_started_hours_up(vehicle_type):
    start = datetime(2026, 1, 5, 10, 0)
    assert WeekdayFee().calculate(start, datetime(2026, 1, 5, 11, 30), vehicle_type) == 20.0
    assert WeekdayFee().calculate(start, datetime(2026, 1, 5, 11, 0), vehicle_type) == 10.0


def test_slab_fees_match_the_published_examples():
    start = datetime(2026, 1, 3, 9, 0)
    fees = [weekend_fee().calculate(start, start.replace(hour=9 + h), VehicleType.CAR) for h in (1, 3, 5, 7)]
    assert fees == [20.0, 70.0, 140.0, 230.0]


def test_slab_boundaries_and_unsorted_slabs():
    start = datetime(2026, 1, 3, 0, 0)
    fee = WeekendSlabFee({VehicleType.CAR: list(reversed(CAR_SLABS))})
    got = {h: fee.calculate(start, start.replace(hour=h), VehicleType.CAR) for h in (2, 4, 6, 12)}
    assert got == {2: 40.0, 4: 100.0, 6: 180.0, 12: 180.0 + 6 * 50.0}
    assert fee.calculate(start, start.replace(minute=30), VehicleType.CAR) == 20.0, "a part hour is a full hour"


def test_factory_picks_weekend_tariff_by_exit_day():
    weekday, weekend = WeekdayFee(), weekend_fee()
    factory = FeeStrategyFactory(weekday, weekend)
    assert factory.for_exit_time(datetime(2026, 1, 3, 12, 0)) is weekend  # Saturday
    assert factory.for_exit_time(datetime(2026, 1, 4, 12, 0)) is weekend  # Sunday
    assert factory.for_exit_time(datetime(2026, 1, 2, 12, 0)) is weekday  # Friday
    assert factory.for_exit_time(datetime(2026, 1, 5, 12, 0)) is weekday  # Monday


def test_holiday_decorator_multiplies_only_on_holidays():
    holiday = datetime(2026, 1, 26, 12, 0)  # a Monday
    start = holiday.replace(hour=10)
    fee = HolidayFee(WeekdayFee(), frozenset({holiday.date()}), 2.0)
    assert fee.calculate(start, holiday, VehicleType.CAR) == 40.0  # 2 started hours * 10 * 2
    other = datetime(2026, 1, 27, 12, 0)
    assert fee.calculate(other.replace(hour=10), other, VehicleType.CAR) == 20.0
    default = HolidayFee(WeekdayFee(), frozenset({holiday.date()}))
    assert default.calculate(start, holiday, VehicleType.CAR) == 30.0, "the default multiplier is 1.5"


def test_holiday_decorator_wraps_any_strategy():
    saturday = datetime(2026, 1, 3, 12, 0)
    start = saturday.replace(hour=9)
    holidays = frozenset({date(2026, 1, 3)})
    inner = HolidayFee(weekend_fee(), holidays, 2.0)
    outer = HolidayFee(inner, holidays, 3.0)
    assert isinstance(inner, FeeStrategy)
    assert inner.calculate(start, saturday, VehicleType.CAR) == 2 * 70.0
    assert outer.calculate(start, saturday, VehicleType.CAR) == 6 * 70.0, "decorators compose"


def test_bill_counts_only_successful_payments():
    bill = Bill(100.0, Spot(1), [Payment(40.0, "cash", PaymentStatus.SUCCESS), Payment(60.0, "upi", PaymentStatus.FAILED)])
    assert bill.total_paid == 40.0
    assert not bill.is_paid
    bill.payments.append(Payment(60.0, "card", PaymentStatus.SUCCESS))
    assert bill.total_paid == 100.0 and bill.is_paid, "total_paid >= amount means paid"
    assert Bill(0.0, Spot(1), []).is_paid


def test_a_failed_payment_does_not_count_and_a_retry_settles_the_bill():
    results = iter([True, False, True])
    service, bill = PaymentService(lambda a, m: next(results)), Bill(500, Spot(1), [])
    service.make_payment(bill, 200, "cash")
    failed = service.make_payment(bill, 300, "upi")
    assert failed.status is PaymentStatus.FAILED
    assert bill.total_paid == 200 and not bill.is_paid and bill.spot.status is SpotStatus.OCCUPIED
    service.make_payment(bill, 300, "upi")
    assert bill.is_paid and bill.spot.status is SpotStatus.AVAILABLE


def test_every_attempt_is_recorded():
    outcomes = iter([False, True])
    service, bill = PaymentService(lambda a, m: next(outcomes)), Bill(100, Spot(1), [])
    p1 = service.make_payment(bill, 100, "card")
    p2 = service.make_payment(bill, 100, "upi")
    assert bill.payments == [p1, p2]
    assert (p1.amount, p1.mode, p1.status) == (100, "card", PaymentStatus.FAILED)
    assert (p2.amount, p2.mode, p2.status) == (100, "upi", PaymentStatus.SUCCESS)


def test_overpayment_is_rejected_before_the_gateway_is_called():
    calls = []
    service = PaymentService(lambda a, m: calls.append(a) or True)
    bill = Bill(100, Spot(1), [])
    with pytest.raises(OverpaymentError):
        service.make_payment(bill, 150, "cash")
    service.make_payment(bill, 60, "cash")
    with pytest.raises(OverpaymentError):
        service.make_payment(bill, 41, "cash")  # only 40 is outstanding
    assert calls == [60], "the gateway must not be called for rejected amounts"
    assert len(bill.payments) == 1, "a rejected payment is not recorded"


def test_paying_exactly_the_outstanding_balance_is_allowed():
    service, bill = PaymentService(lambda a, m: True), Bill(100, Spot(1), [])
    service.make_payment(bill, 70, "cash")
    assert bill.spot.status is SpotStatus.OCCUPIED, "not settled yet"
    service.make_payment(bill, 30, "cash")
    assert bill.is_paid and bill.spot.status is SpotStatus.AVAILABLE
