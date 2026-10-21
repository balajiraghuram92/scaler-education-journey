from ecom.exceptions import OrderCannotBeCancelledError, OrderNotFoundError, UserNotFoundError
from ecom.models import Order, OrderItem, OrderStatus, User
from ecom.services.order_service import OrderService
from ecom.store import Store

class OrderServiceImpl(OrderService):

    def __init__(self, store: Store) -> None:
        """Keep the store."""
        raise NotImplementedError('TODO: implement __init__')

    def cancel_order(self, user_id: int, order_id: int) -> Order:
        """Inside store.transaction(): UserNotFoundError for an unknown user; OrderNotFoundError unless an order with this id belongs to the user; OrderCannotBeCancelledError unless its status is PLACED. Then add each OrderItem quantity back to that product's inventory and set the status to CANCELLED."""
        raise NotImplementedError('TODO: implement cancel_order')
