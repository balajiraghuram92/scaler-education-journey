from ecom.exceptions import OrderCannotBeCancelledError, OrderNotFoundError, UserNotFoundError
from ecom.models import Order, OrderItem, OrderStatus, User
from ecom.services.order_service import OrderService
from ecom.store import Store


class OrderServiceImpl(OrderService):
    def __init__(self, store: Store) -> None:
        self.store = store

    def cancel_order(self, user_id: int, order_id: int) -> Order:
        # The transaction holds the store lock: two concurrent cancellations cannot both see PLACED.
        with self.store.transaction():
            user = self.store.get(User, user_id)
            if user is None:
                raise UserNotFoundError("User not found")

            order = self.store.first(Order, id=order_id, user=user)
            if order is None:
                raise OrderNotFoundError("Order not found")

            if order.order_status is not OrderStatus.PLACED:
                raise OrderCannotBeCancelledError(
                    f"Order cannot be cancelled as its status is {order.order_status.value}")

            for item in self.store.find(OrderItem, order=order):
                inventory = self.store.inventory_of(item.product.id)
                if inventory is not None:
                    inventory.quantity += item.quantity

            order.order_status = OrderStatus.CANCELLED
            return order
