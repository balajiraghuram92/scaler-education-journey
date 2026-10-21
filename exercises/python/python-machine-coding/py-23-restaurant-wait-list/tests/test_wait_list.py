from datetime import datetime

import pytest

from controllers.wait_list_controller import WaitListController
from dtos.add_user_to_wait_list_request_dto import AddUserToWaitListRequestDto
from dtos.get_user_wait_list_request_dto import GetUserWaitListRequestDto
from dtos.response_status import ResponseStatus
from dtos.update_wait_list_request_dto import UpdateWaitListRequestDto
from exceptions.unauthorized_access_exception import UnauthorizedAccessException
from exceptions.user_not_found_exception import UserNotFoundException
from models.user import User
from models.user_type import UserType
from models.wait_list_position import WaitListPosition
from repositories.user_repository_impl import UserRepositoryImpl
from repositories.wait_list_position_repository_impl import WaitListPositionRepositoryImpl
from services.wait_list_service_impl import WaitListServiceImpl


class World:
    def __init__(self, customers=4):
        self.users = UserRepositoryImpl()
        self.waits = WaitListPositionRepositoryImpl()
        self.service = WaitListServiceImpl(self.users, self.waits)
        self.controller = WaitListController(self.service)
        self.admin = self.users.save(User("boss", UserType.ADMIN))
        self.customers = [self.users.save(User(f"c{i}", UserType.USER)) for i in range(customers)]


def test_users_get_consecutive_positions_in_order():
    w = World()
    positions = [w.service.add_user_to_wait_list(c.id) for c in w.customers]
    assert positions == [1, 2, 3, 4]
    assert [w.service.get_wait_list_position(c.id) for c in w.customers] == [1, 2, 3, 4]


def test_adding_twice_returns_existing_position():
    w = World()
    a, b = w.customers[:2]
    w.service.add_user_to_wait_list(a.id)
    w.service.add_user_to_wait_list(b.id)
    assert w.service.add_user_to_wait_list(a.id) == 1, "a is already first"
    assert w.service.add_user_to_wait_list(b.id) == 2
    assert len(w.waits.find_all()) == 2, "no duplicate entries"


def test_unknown_user_cannot_join_or_query():
    w = World()
    with pytest.raises(UserNotFoundException, match="User not found"):
        w.service.add_user_to_wait_list(999)
    with pytest.raises(UserNotFoundException, match="User not found"):
        w.service.get_wait_list_position(999)
    assert w.waits.find_all() == []


def test_position_of_user_not_waiting_is_minus_one():
    w = World()
    assert w.service.get_wait_list_position(w.customers[0].id) == -1


def test_admin_removes_from_the_front():
    w = World()
    for c in w.customers:
        w.service.add_user_to_wait_list(c.id)
    w.service.update_wait_list(w.admin.id, 2)
    assert w.service.get_wait_list_position(w.customers[0].id) == -1
    assert w.service.get_wait_list_position(w.customers[1].id) == -1
    assert w.service.get_wait_list_position(w.customers[2].id) == 1, "positions shift forward"
    assert w.service.get_wait_list_position(w.customers[3].id) == 2


def test_removing_more_than_the_list_empties_it():
    w = World(2)
    for c in w.customers:
        w.service.add_user_to_wait_list(c.id)
    w.service.update_wait_list(w.admin.id, 50)
    assert w.waits.find_all() == []
    w.service.update_wait_list(w.admin.id, 3)  # empty list: still fine
    assert w.service.add_user_to_wait_list(w.customers[1].id) == 1


def test_non_admin_is_denied():
    w = World()
    for c in w.customers:
        w.service.add_user_to_wait_list(c.id)
    with pytest.raises(UnauthorizedAccessException, match="Access Denied"):
        w.service.update_wait_list(w.customers[0].id, 1)
    assert len(w.waits.find_all()) == 4


def test_update_unknown_user():
    w = World()
    with pytest.raises(UserNotFoundException, match="User not found"):
        w.service.update_wait_list(999, 1)


def test_controller_success_responses():
    w = World()
    add = w.controller.add_user_to_wait_list(AddUserToWaitListRequestDto(w.customers[0].id))
    assert add.response_status is ResponseStatus.SUCCESS and add.position == 1
    w.controller.add_user_to_wait_list(AddUserToWaitListRequestDto(w.customers[1].id))
    get = w.controller.get_wait_list_status(GetUserWaitListRequestDto(w.customers[1].id))
    assert get.response_status is ResponseStatus.SUCCESS and get.position == 2
    upd = w.controller.update_wait_list(UpdateWaitListRequestDto(w.admin.id, 1))
    assert upd.response_status is ResponseStatus.SUCCESS
    assert w.controller.get_wait_list_status(GetUserWaitListRequestDto(w.customers[1].id)).position == 1


def test_controller_never_raises():
    w = World()
    add = w.controller.add_user_to_wait_list(AddUserToWaitListRequestDto(999))
    assert add.response_status is ResponseStatus.FAILURE and add.position == 0
    get = w.controller.get_wait_list_status(GetUserWaitListRequestDto(999))
    assert get.response_status is ResponseStatus.FAILURE and get.position == 0
    denied = w.controller.update_wait_list(UpdateWaitListRequestDto(w.customers[0].id, 1))
    assert denied.response_status is ResponseStatus.FAILURE
    assert w.controller.update_wait_list(UpdateWaitListRequestDto(999, 1)).response_status is ResponseStatus.FAILURE


def test_wait_list_repository_keeps_order():
    users = UserRepositoryImpl()
    repo = WaitListPositionRepositoryImpl()
    entries = [repo.save(WaitListPosition(users.save(User(f"u{i}", UserType.USER)), datetime.now())) for i in range(3)]
    assert [e.id for e in entries] == [1, 2, 3]
    assert repo.find_all() == entries
    snapshot = repo.find_all()
    snapshot.clear()
    assert len(repo.find_all()) == 3, "find_all must return a copy"
    assert repo.delete(entries[0]) is entries[0]
    assert repo.find_all() == entries[1:]
