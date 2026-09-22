from ecom.models.order import Order
from .order_service import OrderService
from django.db.transaction import atomic
from ecom.models import User, Order, OrderItem, Product, Inventory
from ecom.exceptions import UserNotFoundError, OrderNotFoundError, OrderCannotBeCancelledError
from ..models.order_status import OrderStatus


class OrderServiceImpl(OrderService):
    @atomic
    def cancel_order(
            self,
            user_id: int,
            order_id: int,
    ) -> Order:

        user = User.objects.filter(pk=user_id).first()

        if user is None:
            raise UserNotFoundError("User not found")

        order = Order.objects.filter(pk=order_id, user=user).first()

        if order is None:
            raise OrderNotFoundError("Order not found")

        if order.order_status != OrderStatus.PLACED.value:
            raise OrderCannotBeCancelledError(f"Order cannot be cancelled as its status is {order.order_status}")

        order_items = OrderItem.objects.filter(order=order).all()

        for order_item in order_items:
            product = order_item.product
            inventory = Inventory.objects.filter(product=product).first()
            inventory.quantity += order_item.quantity
            inventory.save()

        order.order_status = OrderStatus.CANCELLED

        order.save()

        return order








