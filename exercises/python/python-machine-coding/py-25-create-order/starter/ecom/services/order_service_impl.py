from typing import List, Tuple
from ecom.exceptions import OutOfStockError, ProductNotFoundError, UserNotFoundError
from ecom.models import Order, OrderItem, Product, User
from ecom.services.order_service import OrderService
from ecom.store import Store

class OrderServiceImpl(OrderService):

    def __init__(self, store: Store) -> None:
        """Keep the store."""
        raise NotImplementedError('TODO: implement __init__')

    def place_order(self, user_id: int, product_ids_with_quantity: List[Tuple[int, int]]) -> Order:
        """Inside store.transaction(): UserNotFoundError for an unknown user; for every product (totalling repeated product ids) ProductNotFoundError if unknown and OutOfStockError if it has no inventory or too little stock. Only then create the PLACED Order, one OrderItem per product, and decrement each inventory."""
        raise NotImplementedError('TODO: implement place_order')
