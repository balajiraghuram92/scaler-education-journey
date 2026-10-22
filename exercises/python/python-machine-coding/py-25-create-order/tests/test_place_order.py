import threading

import pytest

from ecom.controllers.order_controller import OrderController
from ecom.dtos import PlaceOrderReqDto, ResponseStatus
from ecom.exceptions import OutOfStockError, ProductNotFoundError, UserNotFoundError
from ecom.models import Inventory, Order, OrderItem, OrderStatus, Product, User
from ecom.services.order_service_impl import OrderServiceImpl
from ecom.store import Store


class World:
    def __init__(self):
        self.store = Store()
        self.user = self.store.add(User("Asha", "asha@example.com"))
        self.phone = self.store.add(Product("Phone"))
        self.case = self.store.add(Product("Case"))
        self.cable = self.store.add(Product("Cable"))  # no inventory row
        self.phone_stock = self.store.add(Inventory(self.phone, 10))
        self.case_stock = self.store.add(Inventory(self.case, 5))
        self.service = OrderServiceImpl(self.store)

    def order(self, *lines):
        return self.service.place_order(self.user.id, list(lines))


def test_place_order_decrements_stock_and_creates_items():
    w = World()
    order = w.order((w.phone.id, 2), (w.case.id, 1))
    assert isinstance(order, Order) and order.id
    assert order.user is w.user and order.order_status is OrderStatus.PLACED
    items = {i.product.name: i.quantity for i in w.store.find(OrderItem, order=order)}
    assert items == {"Phone": 2, "Case": 1}
    assert w.store.inventory_of(w.phone.id).quantity == 8
    assert w.store.inventory_of(w.case.id).quantity == 4


def test_unknown_user_is_rejected():
    w = World()
    with pytest.raises(UserNotFoundError):
        w.service.place_order(999, [(w.phone.id, 1)])
    assert w.store.find(Order) == []
    assert w.store.inventory_of(w.phone.id).quantity == 10


def test_unknown_product_is_rejected():
    w = World()
    with pytest.raises(ProductNotFoundError):
        w.order((w.phone.id, 1), (999, 1))
    assert w.store.inventory_of(w.phone.id).quantity == 10


def test_out_of_stock_and_exact_stock_boundary():
    w = World()
    with pytest.raises(OutOfStockError):
        w.order((w.case.id, 6))
    w.order((w.case.id, 5))  # exactly the stock is fine
    assert w.store.inventory_of(w.case.id).quantity == 0
    with pytest.raises(OutOfStockError):
        w.order((w.case.id, 1))


def test_failed_order_changes_nothing():
    w = World()
    with pytest.raises(OutOfStockError):
        w.order((w.phone.id, 3), (w.case.id, 99))
    assert w.store.inventory_of(w.phone.id).quantity == 10, "the first product must not be decremented"
    assert w.store.inventory_of(w.case.id).quantity == 5
    assert w.store.find(Order) == [] and w.store.find(OrderItem) == []


def test_product_without_inventory_is_out_of_stock():
    w = World()
    with pytest.raises(OutOfStockError):
        w.order((w.cable.id, 1))


def test_same_product_on_two_lines_is_counted_together():
    w = World()
    with pytest.raises(OutOfStockError):
        w.order((w.case.id, 3), (w.case.id, 3))  # 6 requested, 5 in stock
    assert w.store.inventory_of(w.case.id).quantity == 5
    order = w.order((w.phone.id, 3), (w.phone.id, 4))
    assert w.store.inventory_of(w.phone.id).quantity == 3
    assert sum(i.quantity for i in w.store.find(OrderItem, order=order)) == 7


def test_concurrent_orders_never_overbook():
    w = World()
    barrier, outcomes, guard = threading.Barrier(20, timeout=10), [], threading.Lock()

    def buy():
        barrier.wait()
        try:
            w.service.place_order(w.user.id, [(w.phone.id, 1)])
            ok = True
        except OutOfStockError:
            ok = False
        with guard:
            outcomes.append(ok)

    threads = [threading.Thread(target=buy) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)
    assert len(outcomes) == 20
    assert outcomes.count(True) == 10, "exactly the 10 units in stock can be sold"
    assert w.store.inventory_of(w.phone.id).quantity == 0
    assert len(w.store.find(Order)) == 10


def test_controller_responses():
    w = World()
    controller = OrderController(w.service)
    ok = controller.place_order(PlaceOrderReqDto(w.user.id, [(w.phone.id, 1)]))
    assert ok.response_status is ResponseStatus.SUCCESS and ok.order.order_status is OrderStatus.PLACED
    for request in (PlaceOrderReqDto(999, [(w.phone.id, 1)]), PlaceOrderReqDto(w.user.id, [(999, 1)]),
                    PlaceOrderReqDto(w.user.id, [(w.case.id, 50)])):
        res = controller.place_order(request)
        assert res.response_status is ResponseStatus.FAILURE, f"expected FAILURE for {request}"
        assert res.order is None
