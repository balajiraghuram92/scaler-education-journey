import pytest

from controllers.booking_controller import BookingController
from dtos.generate_invoice_request_dto import GenerateInvoiceRequestDto
from dtos.response_status import ResponseStatus
from exceptions.customer_session_not_found_exception import CustomerSessionNotFoundError
from models.booking import Booking
from models.customer_session import CustomerSession
from models.customer_session_status import CustomerSessionStatus
from models.room import Room
from models.user import User
from repositories.booking_repository_impl import BookingRepositoryImpl
from repositories.customer_session_repository_impl import CustomerSessionRepositoryImpl
from services.booking_service_impl import BookingServiceImpl


def make_room(room_id, price):
    r = Room()
    r.id = room_id
    r.price = price
    return r


def make_user(user_id):
    u = User()
    u.id = user_id
    return u


@pytest.fixture
def w():
    class W:
        pass

    w = W()
    w.sessions = CustomerSessionRepositoryImpl()
    w.bookings = BookingRepositoryImpl()
    w.service = BookingServiceImpl(w.sessions, w.bookings)
    w.controller = BookingController(w.service)
    w.r1 = make_room(1, 1000.0)
    w.r2 = make_room(2, 500.0)

    def open_session(user_id):
        s = CustomerSession()
        s.user = make_user(user_id)
        s.customer_session_status = CustomerSessionStatus.ACTIVE
        return w.sessions.save(s)

    def book(session, rooms):
        b = Booking()
        b.customer_session = session
        b.booked_rooms = dict(rooms)
        return w.bookings.save(b)

    w.open_session = open_session
    w.book = book
    return w


def approx(x):
    return pytest.approx(x, rel=1e-9)


def test_single_booking_totals(w):
    s = w.open_session(1)
    w.book(s, {w.r1: 2})
    invoice = w.service.generate_invoice(1)
    assert invoice.total_amount == approx(2000.0)
    assert invoice.gst == approx(360.0), "GST is 18% of the total"
    assert invoice.service_charge == approx(200.0), "service charge is 10% of the total"
    assert invoice.booked_rooms == {w.r1: 2}


def test_rooms_are_aggregated_across_bookings(w):
    s = w.open_session(1)
    w.book(s, {w.r1: 2})
    w.book(s, {w.r1: 3})
    invoice = w.service.generate_invoice(1)
    assert invoice.booked_rooms == {w.r1: 5}, "days for the same room must be summed"
    assert invoice.total_amount == approx(5000.0)


def test_multiple_rooms_total(w):
    s = w.open_session(1)
    w.book(s, {w.r1: 1, w.r2: 4})
    w.book(s, {w.r2: 1})
    invoice = w.service.generate_invoice(1)
    assert invoice.booked_rooms == {w.r1: 1, w.r2: 5}
    assert invoice.total_amount == approx(1000.0 + 5 * 500.0)
    assert invoice.gst == approx(invoice.total_amount * 0.18)


def test_session_is_ended_after_invoice(w):
    s = w.open_session(1)
    w.book(s, {w.r1: 1})
    w.service.generate_invoice(1)
    assert s.customer_session_status is CustomerSessionStatus.ENDED
    assert w.sessions.find_active_customer_session_by_user_id(1) is None


def test_second_invoice_fails_because_session_ended(w):
    s = w.open_session(1)
    w.book(s, {w.r1: 1})
    w.service.generate_invoice(1)
    with pytest.raises(CustomerSessionNotFoundError):
        w.service.generate_invoice(1)


def test_no_active_session_raises(w):
    with pytest.raises(CustomerSessionNotFoundError):
        w.service.generate_invoice(42)


def test_empty_session_gives_zero_invoice(w):
    w.open_session(1)
    invoice = w.service.generate_invoice(1)
    assert invoice.total_amount == 0
    assert invoice.gst == 0 and invoice.service_charge == 0
    assert invoice.booked_rooms == {}


def test_only_this_sessions_bookings_are_billed(w):
    mine = w.open_session(1)
    other = w.open_session(2)
    w.book(mine, {w.r1: 1})
    w.book(other, {w.r1: 7})
    invoice = w.service.generate_invoice(1)
    assert invoice.total_amount == approx(1000.0), "bookings from another user's session must not be billed"
    assert other.is_active(), "the other session must stay active"


def test_controller_responses(w):
    s = w.open_session(1)
    w.book(s, {w.r2: 2})
    req = GenerateInvoiceRequestDto()
    req.user_id = 1
    ok = w.controller.generate_invoice(req)
    assert ok.response_status is ResponseStatus.SUCCESS
    assert ok.invoice.total_amount == approx(1000.0)
    again = w.controller.generate_invoice(req)
    assert again.response_status is ResponseStatus.FAILURE
    assert again.invoice is None


def test_booking_repository_finds_by_session(w):
    s1, s2 = w.open_session(1), w.open_session(2)
    b1 = w.book(s1, {w.r1: 1})
    w.book(s2, {w.r1: 1})
    b3 = w.book(s1, {w.r2: 1})
    found = w.bookings.find_booking_by_customer_session(s1.id)
    assert found == [b1, b3]
    assert w.bookings.find_booking_by_customer_session(999) == []
    assert b1.id == 1 and b3.id == 3
