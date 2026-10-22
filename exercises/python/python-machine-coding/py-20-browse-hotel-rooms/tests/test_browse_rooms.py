import pytest

from controllers.room_controller import RoomController
from dtos.get_rooms_request_dto import GetRoomsRequestDto
from dtos.response_status import ResponseStatus
from models.room import Room
from models.room_type import RoomType
from repositories.room_repository_impl import RoomRepositoryImpl
from services.room_service_impl import RoomServiceImpl


def room(number, room_type, price=100.0):
    r = Room()
    r.room_number = number
    r.room_type = room_type
    r.price = price
    return r


@pytest.fixture
def world():
    repo = RoomRepositoryImpl()
    for r in [room("101", RoomType.DELUXE), room("102", RoomType.SUITE), room("103", RoomType.DELUXE),
              room("104", RoomType.SUPER_DELUXE)]:
        repo.save(r)
    service = RoomServiceImpl(repo)
    return repo, service, RoomController(service)


def request(room_type):
    req = GetRoomsRequestDto()
    req.room_type = room_type
    return req


def numbers(rooms):
    return sorted(r.room_number for r in rooms)


def test_no_filter_returns_all_rooms(world):
    _, _, controller = world
    response = controller.get_rooms(request(None))
    assert response.response_status is ResponseStatus.SUCCESS
    assert numbers(response.rooms) == ["101", "102", "103", "104"]


def test_empty_string_returns_all_rooms(world):
    _, _, controller = world
    response = controller.get_rooms(request(""))
    assert response.response_status is ResponseStatus.SUCCESS
    assert len(response.rooms) == 4


@pytest.mark.parametrize("text,expected", [("deluxe", ["101", "103"]), ("suite", ["102"]),
                                           ("super_deluxe", ["104"])])
def test_filter_by_each_type(world, text, expected):
    _, _, controller = world
    response = controller.get_rooms(request(text))
    assert response.response_status is ResponseStatus.SUCCESS
    assert numbers(response.rooms) == expected


def test_no_rooms_of_type_returns_empty_list():
    repo = RoomRepositoryImpl()
    repo.save(room("1", RoomType.DELUXE))
    controller = RoomController(RoomServiceImpl(repo))
    response = controller.get_rooms(request("suite"))
    assert response.response_status is ResponseStatus.SUCCESS
    assert response.rooms == []


def test_invalid_type_makes_controller_fail(world):
    _, _, controller = world
    response = controller.get_rooms(request("penthouse"))
    assert response.response_status is ResponseStatus.FAILURE
    assert response.rooms == []


def test_service_rejects_invalid_type(world):
    _, service, _ = world
    with pytest.raises(Exception):
        service.get_rooms("penthouse")


def test_repository_assigns_ids_and_stores_rooms():
    repo = RoomRepositoryImpl()
    a = repo.save(room("1", RoomType.SUITE))
    b = repo.add(room("2", RoomType.SUITE))
    assert (a.id, b.id) == (1, 2)
    assert repo.get_rooms() == [a, b]
    assert repo.get_rooms_by_room_type(RoomType.SUITE) == [a, b]
    assert repo.get_rooms_by_room_type(RoomType.DELUXE) == []
