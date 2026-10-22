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
    def __init__(self, 
                 user_repo: UserRepository, 
                 room_repo: RoomRepository, 
                 session_repo: CustomerSessionRepository, 
                 booking_repo: BookingRepository):
        self.user_repo = user_repo
        self.room_repo = room_repo
        self.session_repo = session_repo
        self.booking_repo = booking_repo

    def make_booking(self, user_id: int, rooms_to_be_booked: Dict[int, int]) -> Booking:
        # 1. Fetch User
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found.")

        # 2. Fetch and Validate Rooms
        actual_rooms = {}
        for room_id, count in rooms_to_be_booked.items():
            room = self.room_repo.find_by_id(room_id)
            if not room:
                raise InvalidRoomException(f"Room with ID {room_id} does not exist.")
            actual_rooms[room] = count

        # 3. Handle Customer Session
        session = self.session_repo.find_active_customer_session_by_user_id(user_id)
        if not session:
            session = CustomerSession()
            session.user = user
            session.customer_session_status = CustomerSessionStatus.ACTIVE
            self.session_repo.save(session)

        # 4. Create and Save Booking
        booking = Booking()
        booking.customer_session = session
        booking.booked_rooms = actual_rooms
        
        return self.booking_repo.save(booking)
