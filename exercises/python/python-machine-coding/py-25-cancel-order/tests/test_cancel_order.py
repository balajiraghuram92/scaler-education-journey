import threading

import pytest

from ecom.controllers.order_controller import OrderController
from ecom.dtos import CancelOrderReqDto, ResponseStatus
from ecom.exceptions import OrderCannotBeCancelledError, OrderNotFoundError, UserNotFoundError
from ecom.models import Inventory, Order, OrderItem, OrderStatus, Product, User
from ecom.services.order_service_impl import OrderServiceImpl
from ecom.store import Store


class World:
    def __init__(self):
        self.store = Store()
        self.asha = self.store.add(User("Asha"))
        self.ravi = self.store.add(User("Ravi"))
        self.phone = self.store.add(Product("Phone"))
        self.case = self.store.add(Product("Case"))
        # stock AFTER the order below was placed: phone 10 - 2, case 5 - 1
        self.store.add(Inventory(self.phone, 8))
        self.store.add(Inventory(self.case, 4))
        self.service = OrderServiceImpl(self.store)
        self.order = self.make_order(self.asha, [(self.phone, 2), (self.case, 1)])

    def make_order(self, user, lines, status=OrderStatus.PLACED):
        order = self.store.add(Order(user, status))
        for product, quantity in lines:
            self.store.add(OrderItem(order, product, quantity))
        return order

    def stock(self, product):
        return self.store.inventory_of(product.id).quantity


def test_cancel_restocks_and_marks_cancelled():
    w = World()
    result = w.service.cancel_order(w.asha.id, w.order.id)
    assert result is w.order and w.order.order_status is OrderStatus.CANCELLED
    assert w.stock(w.phone) == 10 and w.stock(w.case) == 5


def test_unknown_user_and_unknown_order():
    w = World()
    with pytest.raises(UserNotFoundError):
        w.service.cancel_order(999, w.order.id)
    with pytest.raises(OrderNotFoundError):
        w.service.cancel_order(w.asha.id, 999)
    assert w.order.order_status is OrderStatus.PLACED and w.stock(w.phone) == 8


def test_order_of_another_user_is_not_found():
    w = World()
    with pytest.raises(OrderNotFoundError):
        w.service.cancel_order(w.ravi.id, w.order.id)
    assert w.order.order_status is OrderStatus.PLACED
    assert w.stock(w.phone) == 8


@pytest.mark.parametrize("status", [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED])
def test_only_placed_orders_can_be_cancelled(status):
    w = World()
    other = w.make_order(w.asha, [(w.phone, 3)], status)
    with pytest.raises(OrderCannotBeCancelledError):
        w.service.cancel_order(w.asha.id, other.id)
    assert other.order_status is status
    assert w.stock(w.phone) == 8, "nothing may be restocked"


def test_cancelling_twice_restocks_once():
    w = World()
    w.service.cancel_order(w.asha.id, w.order.id)
    with pytest.raises(OrderCannotBeCancelledError):
        w.service.cancel_order(w.asha.id, w.order.id)
    assert w.stock(w.phone) == 10 and w.stock(w.case) == 5


def test_concurrent_cancellations_restock_once():
    w = World()
    barrier, outcomes, guard = threading.Barrier(8, timeout=10), [], threading.Lock()

    def cancel():
        barrier.wait()
        try:
            w.service.cancel_order(w.asha.id, w.order.id)
            ok = True
        except OrderCannotBeCancelledError:
            ok = False
        with guard:
            outcomes.append(ok)

    threads = [threading.Thread(target=cancel) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)
    assert len(outcomes) == 8
    assert outcomes.count(True) == 1, "exactly one cancellation may win"
    assert w.stock(w.phone) == 10 and w.stock(w.case) == 5, "stock restored exactly once"


def test_controller_responses():
    w = World()
    controller = OrderController(w.service)
    ok = controller.cancel_order(CancelOrderReqDto(w.asha.id, w.order.id))
    assert ok.response_status is ResponseStatus.SUCCESS and ok.order is w.order
    for request in (CancelOrderReqDto(999, w.order.id), CancelOrderReqDto(w.asha.id, 999),
                    CancelOrderReqDto(w.asha.id, w.order.id)):  # the last one is already cancelled
        res = controller.cancel_order(request)
        assert res.response_status is ResponseStatus.FAILURE, f"expected FAILURE for {request}"
        assert res.order is None
