import pytest

from controllers.booking_controller import BookingController
from dtos.make_booking_request_dto import MakeBookingRequestDto
from dtos.response_status import ResponseStatus
from exceptions.invalid_room_exception import InvalidRoomException
from exceptions.user_not_found_exception import UserNotFoundException
from models.booking import Booking
from models.customer_session_status import CustomerSessionStatus
from models.room import Room
from models.user import User
from repositories.booking_repository_impl import BookingRepositoryImpl
from repositories.customer_session_repository_impl import CustomerSessionRepositoryImpl
from repositories.room_repository_impl import RoomRepositoryImpl
from repositories.user_repository_impl import UserRepositoryImpl
from services.booking_service_impl import BookingServiceImpl


class World:
    def __init__(self):
        self.users = UserRepositoryImpl()
        self.rooms = RoomRepositoryImpl()
        self.sessions = CustomerSessionRepositoryImpl()
        self.bookings = BookingRepositoryImpl()
        self.service = BookingServiceImpl(self.users, self.rooms, self.sessions, self.bookings)
        self.controller = BookingController(self.service)
        self.asha = self.users.save(self._user("Asha"))
        self.ravi = self.users.save(self._user("Ravi"))
        self.r1 = self.rooms.save(self._room("101", 100.0))
        self.r2 = self.rooms.save(self._room("102", 200.0))

    @staticmethod
    def _user(name):
        u = User()
        u.name = name
        return u

    @staticmethod
    def _room(number, price):
        r = Room()
        r.room_number = number
        r.price = price
        return r


@pytest.fixture
def w():
    return World()


def test_first_booking_creates_active_session(w):
    booking = w.service.make_booking(w.asha.id, {w.r1.id: 2})
    assert isinstance(booking, Booking)
    assert booking.customer_session is not None
    assert booking.customer_session.user is w.asha
    assert booking.customer_session.customer_session_status is CustomerSessionStatus.ACTIVE
    assert w.sessions.find_active_customer_session_by_user_id(w.asha.id) is booking.customer_session


def test_booking_contains_real_room_objects(w):
    booking = w.service.make_booking(w.asha.id, {w.r1.id: 2, w.r2.id: 3})
    assert booking.booked_rooms == {w.r1: 2, w.r2: 3}
    assert all(isinstance(r, Room) for r in booking.booked_rooms)
    assert booking.id != 0, "the booking must be saved"


def test_second_booking_reuses_active_session(w):
    first = w.service.make_booking(w.asha.id, {w.r1.id: 1})
    second = w.service.make_booking(w.asha.id, {w.r2.id: 1})
    assert first.customer_session is second.customer_session, "no second session while one is ACTIVE"
    assert len(w.sessions.sessions) == 1
    assert len(w.bookings.bookings) == 2


def test_ended_session_is_not_reused(w):
    first = w.service.make_booking(w.asha.id, {w.r1.id: 1})
    first.customer_session.customer_session_status = CustomerSessionStatus.ENDED
    second = w.service.make_booking(w.asha.id, {w.r1.id: 1})
    assert second.customer_session is not first.customer_session
    assert second.customer_session.is_active()


def test_sessions_are_per_user(w):
    a = w.service.make_booking(w.asha.id, {w.r1.id: 1})
    r = w.service.make_booking(w.ravi.id, {w.r1.id: 1})
    assert a.customer_session is not r.customer_session
    assert a.customer_session.user is w.asha and r.customer_session.user is w.ravi


def test_unknown_user_raises_and_stores_nothing(w):
    with pytest.raises(UserNotFoundException):
        w.service.make_booking(999, {w.r1.id: 1})
    assert w.sessions.sessions == {} and w.bookings.bookings == {}


def test_invalid_room_is_atomic(w):
    with pytest.raises(InvalidRoomException):
        w.service.make_booking(w.asha.id, {w.r1.id: 1, 12345: 1})
    assert w.sessions.sessions == {}, "no session may be created when validation fails"
    assert w.bookings.bookings == {}, "no booking may be stored when validation fails"


def make_request(user_id, rooms):
    req = MakeBookingRequestDto()
    req.user_id = user_id
    req.booked_rooms = rooms
    return req


def test_controller_success(w):
    response = w.controller.make_booking(make_request(w.asha.id, {w.r1.id: 2}))
    assert response.response_status is ResponseStatus.SUCCESS
    assert response.booking.booked_rooms == {w.r1: 2}


def test_controller_failures(w):
    for req in (make_request(999, {w.r1.id: 1}), make_request(w.asha.id, {4242: 1})):
        response = w.controller.make_booking(req)
        assert response.response_status is ResponseStatus.FAILURE
        assert response.booking is None
