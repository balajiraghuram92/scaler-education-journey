import unittest
from models import User
from models import UserType
from models import RoomType
from controllers import RoomController
from repositories import RoomRepository
from repositories import UserRepository
from services import RoomService
from dtos import AddRoomRequestDto
from dtos import AddRoomResponseDto
from dtos import ResponseStatus


class RoomsControllerTest(unittest.TestCase):
    def setUp(self):
        self._room_repository = self.initialize_room_repository()
        self._user_repository = self.initialize_user_repository()
        self._room_service = self.initialize_room_service(self._room_repository, self._user_repository)
        self._rooms_controller = self.initialize_room_controller(self._room_service)

    def initialize_room_repository(self) -> RoomRepository:
        if len(RoomRepository.__subclasses__()) < 1:
            raise Exception("No implementation for " + "RoomRepository")

        return RoomRepository.__subclasses__()[0]()

    def initialize_user_repository(self) -> UserRepository:
        if len(UserRepository.__subclasses__()) < 1:
            raise Exception("No implementation for " + "UserRepository")

        return UserRepository.__subclasses__()[0]()

    def initialize_room_service(self, room_repository: RoomRepository, user_repository: UserRepository) -> RoomService:
        if len(RoomService.__subclasses__()) < 1:
            raise Exception("No implementation for " + "RoomService")

        return RoomService.__subclasses__()[0](room_repository, user_repository)

    def initialize_room_controller(self, room_service: RoomService):
        return RoomController(room_service)

    def testAddRoomSuccess(self):
        admin_user = User(
            name="admin",
            password="aadmin",
            phone="1234567890",
            user_type=UserType.ADMIN
        )

        self._user_repository.save(admin_user)

        request_dto = AddRoomRequestDto(
            user_id=admin_user.id,
            room_name="A1",
            description="Room number A1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        response_dto: AddRoomResponseDto = self._rooms_controller.add_room(request_dto)
        self.assertEqual(response_dto.response_status, ResponseStatus.SUCCESS)
        self.assertIsNotNone(response_dto.room)

    def testAddRoomFailure(self):
        customer = User(
            name="user",
            password="user",
            phone="1234567890",
            user_type=UserType.CUSTOMER
        )

        self._user_repository.save(customer)

        request_dto = AddRoomRequestDto(
            user_id=customer.id,
            room_name="A1",
            description="Room number A1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        response_dto: AddRoomResponseDto = self._rooms_controller.add_room(request_dto)
        self.assertEqual(response_dto.response_status, ResponseStatus.FAILURE)
        self.assertIsNone(response_dto.room)



if __name__ == '__main__':
    unittest.main()



