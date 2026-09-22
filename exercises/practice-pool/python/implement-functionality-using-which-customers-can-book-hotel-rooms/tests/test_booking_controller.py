import unittest
from models import Room
from models import User
from models import UserType
from models import RoomType
from controllers import BookingController
from repositories import RoomRepository
from repositories import UserRepository
from repositories import BookingRepository
from repositories import CustomerSessionRepository
from services import BookingService
from dtos import MakeBookingResponseDto
from dtos import MakeBookingRequestDto
from dtos import ResponseStatus


class RoomsControllerTest(unittest.TestCase):

    def setUp(self):
        self._room_repository = self.initialize_repository(RoomRepository)
        self._user_repository = self.initialize_repository(UserRepository)
        self._booking_repository = self.initialize_repository(BookingRepository)
        self._customer_session_repository = self.initialize_repository(CustomerSessionRepository)
        self._booking_service = self.initialize_booking_service(
            self._room_repository,
            self._user_repository,
            self._customer_session_repository,
            self._booking_repository
        )
        self._booking_controller = self.initialize_booking_controller(self._booking_service)

    def initialize_repository(self, kls):
        if len(kls.__subclasses__()) < 1:
            raise Exception("No implementation for " + kls.__name__)

        return kls.__subclasses__()[0]()
    
    def initialize_booking_service(
            self,
            room_repository: RoomRepository,
            user_repository: UserRepository,
            customer_session_repository: CustomerSessionRepository,
            booking_repository: BookingRepository

    ) -> BookingService:
        if len(BookingService.__subclasses__()) < 1:
            raise Exception("No implementation for " + "RoomService")

        return BookingService.__subclasses__()[0](
            room_repository,
            user_repository,
            customer_session_repository,
            booking_repository
        )

    def initialize_booking_controller(self, booking_service: BookingService):
        return BookingController(booking_service)

    def testBookRoomSuccess(self):
        user = self.add_user()
        rooms = self.add_rooms()

        request_dto = MakeBookingRequestDto(
            rooms_to_be_booked=[
                [rooms[0].id, 2],
                [rooms[1].id, 1]
            ],
            user_id=user.id
        )

        response_dto: MakeBookingResponseDto = self._booking_controller.make_booking(
            request_dto
        )

        self.assertEqual(len(response_dto.booking.booked_rooms), 2)
        self.assertEqual(response_dto.response_status, ResponseStatus.SUCCESS)

    def testBookRoomUserDoesntExists(self):
        user = self.add_user()
        rooms = self.add_rooms()

        request_dto = MakeBookingRequestDto(
            rooms_to_be_booked=[
                [rooms[0].id, 2],
                [rooms[1].id, 1]
            ],
            user_id=user.id + 1
        )

        response_dto: MakeBookingResponseDto = self._booking_controller.make_booking(
            request_dto
        )

        self.assertIsNone(response_dto.booking)
        self.assertEqual(response_dto.response_status, ResponseStatus.FAILURE)

    def testBookRoomInvalidRoom(self):
        user = self.add_user()

        # requesting for rooms that are not present with id 100, 101
        request_dto = MakeBookingRequestDto(
            rooms_to_be_booked=[
                [100, 2],
                [101, 1]
            ],
            user_id=user.id + 1
        )

        response_dto: MakeBookingResponseDto = self._booking_controller.make_booking(
            request_dto
        )

        self.assertIsNone(response_dto.booking)
        self.assertEqual(response_dto.response_status, ResponseStatus.FAILURE)

    def add_user(self):
        user = User(
            name="Test User",
            password="123456",
            phone="9999999999",
            user_type=UserType.CUSTOMER
        )

        return self._user_repository.save(user)

    def add_rooms(self):

        rooms = []

        room = Room(
            room_name="A1",
            description="Room number A1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        self._room_repository.save(room)
        rooms.append(room)

        room = Room(
            room_name="A2",
            description="Room number A2",
            price=7000.0,
            room_type=RoomType.SUPER_DELUXE
        )

        self._room_repository.save(room)
        rooms.append(room)

        room = Room(
            room_name="A3",
            description="Room number A3",
            price=9000.0,
            room_type=RoomType.SUITE
        )

        self._room_repository.save(room)
        rooms.append(room)

        room = Room(
            room_name="B1",
            description="Room number B1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        self._room_repository.save(room)
        rooms.append(room)

        room = Room(
            room_name="B2",
            description="Room number B2",
            price=7000.0,
            room_type=RoomType.SUPER_DELUXE
        )

        self._room_repository.save(room)
        rooms.append(room)

        room = Room(
            room_name="B3",
            description="Room number B3",
            price=9000.0,
            room_type=RoomType.SUITE
        )

        self._room_repository.save(room)
        rooms.append(room)

        return rooms


if __name__ == '__main__':
    unittest.main()


