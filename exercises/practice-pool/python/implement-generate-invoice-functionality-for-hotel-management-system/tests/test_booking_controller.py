import unittest

from models import Booking
from models import CustomerSession
from models import CustomerSessionStatus
from models import Room
from models import User
from models import UserType
from models import RoomType
from controllers import BookingController
from repositories import BookingRepository
from repositories import CustomerSessionRepository
from services import BookingService
from dtos import GenerateInvoiceResponseDto
from dtos import GenerateInvoiceRequestDto
from dtos import ResponseStatus


class RoomsControllerTest(unittest.TestCase):

    def setUp(self):
        self._booking_repository = self.initialize_repository(BookingRepository)
        self._customer_session_repository = self.initialize_repository(CustomerSessionRepository)
        self._booking_service = self.initialize_booking_service(
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
            customer_session_repository: CustomerSessionRepository,
            booking_repository: BookingRepository

    ) -> BookingService:
        if len(BookingService.__subclasses__()) < 1:
            raise Exception("No implementation for " + "RoomService")

        return BookingService.__subclasses__()[0](
            customer_session_repository,
            booking_repository
        )

    def initialize_booking_controller(self, booking_service: BookingService):
        return BookingController(booking_service)

    def testGenerateInvoiceSuccess1(self):
        user = self.add_user()
        rooms = self.add_rooms()

        customer_session: CustomerSession= CustomerSession(
            user=user,
            customer_session_status=CustomerSessionStatus.ACTIVE
        )

        self._customer_session_repository.save(customer_session)

        booked_rooms = [
            [rooms[0], 2],
            [rooms[1], 1]
        ]

        booking = Booking(
            customer_session=customer_session,
            booked_rooms=booked_rooms
        )

        self._booking_repository.save(booking)

        request_dto = GenerateInvoiceRequestDto(
            user_id=user.id
        )

        response_dto: GenerateInvoiceResponseDto = self._booking_controller.generate_invoice(
            request_dto
        )

        self.assertEqual(len(response_dto.invoice.booked_rooms), 2)
        self.assertEqual(response_dto.response_status, ResponseStatus.SUCCESS)

    def testGenerateInvoiceForInvalidCustomerSession(self):
        user = self.add_user()
        rooms = self.add_rooms()

        customer_session: CustomerSession= CustomerSession(
            user=user,
            customer_session_status=CustomerSessionStatus.ACTIVE
        )

        self._customer_session_repository.save(customer_session)

        booked_rooms = [
            [rooms[0], 2],
            [rooms[1], 1]
        ]

        booking = Booking(
            customer_session=customer_session,
            booked_rooms=booked_rooms
        )

        self._booking_repository.save(booking)

        request_dto = GenerateInvoiceRequestDto(
            user_id=user.id + 1
        )

        response_dto: GenerateInvoiceResponseDto = self._booking_controller.generate_invoice(
            request_dto
        )

        self.assertIsNone(response_dto.invoice)
        self.assertEqual(response_dto.response_status, ResponseStatus.FAILURE)

    def add_user(self):
        user = User(
            id=1,
            name="Test User",
            password="123456",
            phone="9999999999",
            user_type=UserType.CUSTOMER
        )

        return user

    def add_rooms(self):

        rooms = []

        room = Room(
            id=1,
            room_name="A1",
            description="Room number A1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        rooms.append(room)

        room = Room(
            id=2,
            room_name="A2",
            description="Room number A2",
            price=7000.0,
            room_type=RoomType.SUPER_DELUXE
        )

        rooms.append(room)

        room = Room(
            id=3,
            room_name="A3",
            description="Room number A3",
            price=9000.0,
            room_type=RoomType.SUITE
        )

        rooms.append(room)

        room = Room(
            id=4,
            room_name="B1",
            description="Room number B1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        rooms.append(room)

        room = Room(
            id=5,
            room_name="B2",
            description="Room number B2",
            price=7000.0,
            room_type=RoomType.SUPER_DELUXE
        )

        rooms.append(room)

        room = Room(
            id=6,
            room_name="B3",
            description="Room number B3",
            price=9000.0,
            room_type=RoomType.SUITE
        )

        rooms.append(room)

        return rooms


if __name__ == '__main__':
    unittest.main()


