import pytest

from controllers.room_controller import RoomController
from dtos.add_room_request_dto import AddRoomRequestDto
from dtos.response_status import ResponseStatus
from exceptions.unauthorized_access import UnauthorizedAccessError
from exceptions.user_not_found_exception import UserNotFoundError
from models.room import Room
from models.room_type import RoomType
from models.user import User
from models.user_type import UserType
from repositories.room_repository_impl import RoomRepositoryImpl
from repositories.user_repository_impl import UserRepositoryImpl
from services.room_service_impl import RoomServiceImpl


@pytest.fixture
def world():
    users = UserRepositoryImpl()
    rooms = RoomRepositoryImpl()
    admin = User()
    admin.name = "Admin"
    admin.user_type = UserType.ADMIN
    customer = User()
    customer.name = "Cust"
    customer.user_type = UserType.CUSTOMER
    users.save(admin)
    users.save(customer)
    service = RoomServiceImpl(users, rooms)
    return {"users": users, "rooms": rooms, "service": service, "controller": RoomController(service),
            "admin": admin, "customer": customer}


def make_request(user_id, room_type="deluxe", name="101", price=2500.0, description="Sea view"):
    req = AddRoomRequestDto()
    req.user_id = user_id
    req.name = name
    req.price = price
    req.room_type = room_type
    req.description = description
    return req


def test_admin_can_add_room(world):
    room = world["service"].add_room(world["admin"].id, "101", 2500.0, "deluxe", "Sea view")
    assert isinstance(room, Room)
    assert room.name == "101" and room.price == 2500.0 and room.description == "Sea view"
    assert room.id != 0, "saved room should have an id"
    assert world["rooms"].get_rooms() == [room]


@pytest.mark.parametrize("text,expected", [("deluxe", RoomType.DELUXE), ("super_deluxe", RoomType.SUPER_DELUXE),
                                           ("suite", RoomType.SUITE)])
def test_room_type_string_is_mapped_to_enum(world, text, expected):
    room = world["service"].add_room(world["admin"].id, "r", 1.0, text, "d")
    assert room.room_type is expected


def test_ids_are_assigned_sequentially(world):
    ids = [world["service"].add_room(world["admin"].id, f"r{i}", 1.0, "suite", "d").id for i in range(3)]
    assert ids == [1, 2, 3]


def test_unknown_user_raises(world):
    with pytest.raises(UserNotFoundError):
        world["service"].add_room(999, "101", 1.0, "deluxe", "d")
    assert world["rooms"].get_rooms() == []


def test_customer_cannot_add_room(world):
    with pytest.raises(UnauthorizedAccessError):
        world["service"].add_room(world["customer"].id, "101", 1.0, "deluxe", "d")
    assert world["rooms"].get_rooms() == [], "nothing may be stored on an unauthorised call"


def test_invalid_room_type_raises_value_error(world):
    with pytest.raises(ValueError):
        world["service"].add_room(world["admin"].id, "101", 1.0, "penthouse", "d")
    assert world["rooms"].get_rooms() == []


def test_controller_success_response(world):
    response = world["controller"].add_room(make_request(world["admin"].id, "suite", "S1", 9000.0))
    assert response.response_status is ResponseStatus.SUCCESS
    assert response.room is not None and response.room.room_type is RoomType.SUITE
    assert response.room.name == "S1"


def test_controller_failure_responses(world):
    bad = [make_request(999), make_request(world["customer"].id), make_request(world["admin"].id, "cabin")]
    for req in bad:
        response = world["controller"].add_room(req)
        assert response.response_status is ResponseStatus.FAILURE, f"expected FAILURE for {req.__dict__}"
        assert response.room is None


def test_repository_filters_by_room_type(world):
    for i, kind in enumerate(["deluxe", "suite", "deluxe"]):
        world["service"].add_room(world["admin"].id, f"r{i}", 1.0, kind, "d")
    deluxe = world["rooms"].get_rooms_by_room_type(RoomType.DELUXE)
    assert [r.name for r in deluxe] == ["r0", "r2"]
    assert world["rooms"].get_rooms_by_room_type(RoomType.SUPER_DELUXE) == []
