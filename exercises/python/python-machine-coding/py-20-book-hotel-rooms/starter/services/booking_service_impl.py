from typing import Dict
from models.booking import Booking
from models.customer_session import CustomerSession
from models.customer_session_status import CustomerSessionStatus
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.invalid_room_exception import InvalidRoomException
from services.booking_service import BookingService
from repositories.user_repository import UserRepository
from repositories.room_repository import RoomRepository
from repositories.customer_session_repository import CustomerSessionRepository
from repositories.booking_repository import BookingRepository

class BookingServiceImpl(BookingService):

    def __init__(self, user_repo: UserRepository, room_repo: RoomRepository, session_repo: CustomerSessionRepository, booking_repo: BookingRepository):
        raise NotImplementedError('TODO: implement __init__')

    def make_booking(self, user_id: int, rooms_to_be_booked: Dict[int, int]) -> Booking:
        """rooms_to_be_booked maps room id to count. Read and validate everything first: user (UserNotFoundException) and every room (InvalidRoomException). Only then reuse or create the ACTIVE session and save the Booking whose booked_rooms maps Room objects to counts. A failure must write nothing."""
        raise NotImplementedError('TODO: implement make_booking')
