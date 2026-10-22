import pytest

from ecom.controllers.inventory_controller import InventoryController
from ecom.dtos import CreateUpdateInventoryReqDto, DeleteInventoryReqDto, ResponseStatus
from ecom.exceptions import ProductNotFoundError, UnauthorizedAccessError, UserNotFoundError
from ecom.models import Inventory, Product, User, UserType
from ecom.services.inventory_service_impl import InventoryServiceImpl
from ecom.store import Store


class World:
    def __init__(self):
        self.store = Store()
        self.admin = self.store.add(User("Boss", user_type=UserType.ADMIN))
        self.customer = self.store.add(User("Cust", user_type=UserType.CUSTOMER))
        self.phone = self.store.add(Product("Phone"))
        self.case = self.store.add(Product("Case"))
        self.service = InventoryServiceImpl(self.store)
        self.controller = InventoryController(self.service)


def test_admin_creates_inventory():
    w = World()
    inventory = w.service.create_or_update_inventory(w.admin.id, w.phone.id, 7)
    assert isinstance(inventory, Inventory)
    assert inventory.product is w.phone and inventory.quantity == 7
    assert w.store.inventory_of(w.phone.id) is inventory, "the row must be stored"


def test_update_replaces_quantity_without_duplicating():
    w = World()
    first = w.service.create_or_update_inventory(w.admin.id, w.phone.id, 7)
    second = w.service.create_or_update_inventory(w.admin.id, w.phone.id, 3)
    assert w.store.inventory_of(w.phone.id).quantity == 3, "replace the quantity, do not add"
    assert second is first or second.id == first.id
    assert len(w.store.find(Inventory)) == 1


def test_user_and_product_validation():
    w = World()
    with pytest.raises(UserNotFoundError):
        w.service.create_or_update_inventory(999, w.phone.id, 1)
    with pytest.raises(UnauthorizedAccessError):
        w.service.create_or_update_inventory(w.customer.id, w.phone.id, 1)
    with pytest.raises(ProductNotFoundError):
        w.service.create_or_update_inventory(w.admin.id, 999, 1)
    assert w.store.find(Inventory) == []


def test_admin_deletes_inventory():
    w = World()
    w.service.create_or_update_inventory(w.admin.id, w.phone.id, 7)
    w.service.create_or_update_inventory(w.admin.id, w.case.id, 2)
    assert w.service.delete_inventory(w.admin.id, w.phone.id) is None
    assert w.store.inventory_of(w.phone.id) is None
    assert w.store.inventory_of(w.case.id).quantity == 2, "other products are untouched"


def test_delete_tolerates_missing_row_and_checks_user():
    w = World()
    w.service.delete_inventory(w.admin.id, w.phone.id)  # no inventory row: not an error
    w.service.create_or_update_inventory(w.admin.id, w.phone.id, 7)
    with pytest.raises(UserNotFoundError):
        w.service.delete_inventory(999, w.phone.id)
    with pytest.raises(UnauthorizedAccessError):
        w.service.delete_inventory(w.customer.id, w.phone.id)
    assert w.store.inventory_of(w.phone.id).quantity == 7


def test_controller_create_or_update_responses():
    w = World()
    ok = w.controller.create_or_update_inventory(CreateUpdateInventoryReqDto(w.admin.id, w.phone.id, 5))
    assert ok.response_status is ResponseStatus.SUCCESS and ok.inventory.quantity == 5
    for request in (CreateUpdateInventoryReqDto(999, w.phone.id, 5),
                    CreateUpdateInventoryReqDto(w.customer.id, w.phone.id, 5),
                    CreateUpdateInventoryReqDto(w.admin.id, 999, 5)):
        res = w.controller.create_or_update_inventory(request)
        assert res.response_status is ResponseStatus.FAILURE, f"expected FAILURE for {request}"
        assert res.inventory is None
    assert w.store.inventory_of(w.phone.id).quantity == 5


def test_controller_delete_responses():
    w = World()
    w.service.create_or_update_inventory(w.admin.id, w.phone.id, 5)
    assert w.controller.delete_inventory(DeleteInventoryReqDto(w.customer.id, w.phone.id)).response_status \
        is ResponseStatus.FAILURE
    assert w.controller.delete_inventory(DeleteInventoryReqDto(999, w.phone.id)).response_status \
        is ResponseStatus.FAILURE
    assert w.store.inventory_of(w.phone.id) is not None
    assert w.controller.delete_inventory(DeleteInventoryReqDto(w.admin.id, w.phone.id)).response_status \
        is ResponseStatus.SUCCESS
    assert w.store.inventory_of(w.phone.id) is None
