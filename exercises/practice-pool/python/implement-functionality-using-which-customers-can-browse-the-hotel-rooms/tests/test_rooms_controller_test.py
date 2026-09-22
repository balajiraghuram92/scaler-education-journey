import unittest
from models import Room, RoomType
from controllers import RoomController
from repositories import RoomRepository
from services import RoomService
from dtos import GetRoomsRequestDto, GetRoomsResponseDto
from dtos import ResponseStatus


class RoomsControllerTest(unittest.TestCase):

    def setUp(self):
        self._room_repository = self.initialize_room_repository()
        self._room_service = self.initialize_room_service(self._room_repository)
        self._rooms_controller = self.initialize_room_controller(self._room_service)

    def initialize_room_repository(self) -> RoomRepository:
        if len(RoomRepository.__subclasses__()) < 1:
            raise Exception("No implementation for {} in package".format(
                RoomRepository.__qualname__
            ))

        return RoomRepository.__subclasses__()[0]()

    def initialize_room_service(self, room_repository: RoomRepository) -> RoomService:
        if len(RoomService.__subclasses__()) < 1:
            raise Exception("No implementation for {} in package".format(
                RoomService.__qualname__
            ))

        return RoomService.__subclasses__()[0](room_repository)

    def initialize_room_controller(self, room_service: RoomService):
        return RoomController(room_service)

    def testGetRoomsWithoutFilter(self):
        self.add_rooms()
        request_dto = GetRoomsRequestDto()
        response = self._rooms_controller.get_rooms(request_dto)
        self.assertEqual(response.response_status, ResponseStatus.SUCCESS)
        self.assertEqual(len(response.rooms), 6)

    def testGetRoomsWithDeluxeFilter(self):
        self.add_rooms()
        request_dto = GetRoomsRequestDto()
        request_dto.room_type = "DELUXE"
        response = self._rooms_controller.get_rooms(request_dto)
        self.assertEqual(response.response_status, ResponseStatus.SUCCESS)
        self.assertEqual(len(response.rooms), 2)

    def testGetRoomsWithSuperDeluxeFilter(self):
        self.add_rooms()
        request_dto = GetRoomsRequestDto()
        request_dto.room_type = "SUPER_DELUXE"
        response = self._rooms_controller.get_rooms(request_dto)
        self.assertEqual(response.response_status, ResponseStatus.SUCCESS)
        self.assertEqual(len(response.rooms), 2)

    def testGetRoomsWithSuiteFilter(self):
        self.add_rooms()
        request_dto = GetRoomsRequestDto()
        request_dto.room_type = "SUITE"
        response = self._rooms_controller.get_rooms(request_dto)
        self.assertEqual(response.response_status, ResponseStatus.SUCCESS)
        self.assertEqual(len(response.rooms), 2)

    def add_rooms(self):

        room = Room(
            room_number="A1",
            description="Room number A1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        self._room_repository.save(room)

        room = Room(
            room_number="A2",
            description="Room number A2",
            price=7000.0,
            room_type=RoomType.SUPER_DELUXE
        )

        self._room_repository.save(room)

        room = Room(
            room_number="A3",
            description="Room number A3",
            price=9000.0,
            room_type=RoomType.SUITE
        )

        self._room_repository.save(room)

        room = Room(
            room_number="B1",
            description="Room number B1",
            price=5000.0,
            room_type=RoomType.DELUXE
        )

        self._room_repository.save(room)

        room = Room(
            room_number="B2",
            description="Room number B2",
            price=7000.0,
            room_type=RoomType.SUPER_DELUXE
        )

        self._room_repository.save(room)

        room = Room(
            room_number="B3",
            description="Room number B3",
            price=9000.0,
            room_type=RoomType.SUITE
        )

        self._room_repository.save(room)


if __name__ == '__main__':
    unittest.main()
