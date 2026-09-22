from typing import List

from models.booking import Booking
from models.customer_session import CustomerSession
from models.customer_session_status import CustomerSessionStatus
from repositories.room_repository import RoomRepository
from repositories.user_repository import UserRepository
from repositories.customer_session_repository import CustomerSessionRepository
from repositories.booking_repository import BookingRepository
from exceptions.user_not_found_error import UserNotFoundError
from exceptions.invalid_room_error import InvalidRoomError
from .booking_service import BookingService


class BookingServiceImpl(BookingService):

    def __init__(
            self,
            room_repository: RoomRepository,
            user_repository: UserRepository,
            customer_session_repository: CustomerSessionRepository,
            booking_repository: BookingRepository
    ):
        super().__init__(
            room_repository,
            user_repository,
            customer_session_repository,
            booking_repository
        )

    def make_booking(self, user_id: int, rooms_to_be_booked: List) -> Booking:
        customer_session = self.customer_session_repository.find_active_customer_session_by_user_id(user_id)
        if customer_session is None:
            user = self.user_repository.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError()
            customer_session = CustomerSession(
                user=user,
                customer_session_status=CustomerSessionStatus.ACTIVE
            )

        booked_rooms = []

        for room_to_be_booked in rooms_to_be_booked:
            room_id, days = room_to_be_booked
            room = self.room_repository.find_by_id(room_id)
            if room is None:
                raise InvalidRoomError()
            booked_rooms.append([room, days])

        booking = Booking(
            customer_session=customer_session,
            booked_rooms=booked_rooms
        )

        return self.booking_repository.save(booking)





