from typing import List, Tuple

from ecom.exceptions import OutOfStockError, ProductNotFoundError, UserNotFoundError
from ecom.models import Order, OrderItem, Product, User
from ecom.services.order_service import OrderService
from ecom.store import Store


class OrderServiceImpl(OrderService):
    def __init__(self, store: Store) -> None:
        self.store = store

    def place_order(self, user_id: int, product_ids_with_quantity: List[Tuple[int, int]]) -> Order:
        # The transaction holds the store lock, so the stock check and the decrement are one atomic step.
        with self.store.transaction():
            user = self.store.get(User, user_id)
            if user is None:
                raise UserNotFoundError("User not found")

            # Total per product first: the same product may appear on several lines.
            requested: dict[int, int] = {}
            for product_id, quantity in product_ids_with_quantity:
                requested[product_id] = requested.get(product_id, 0) + quantity

            lines = []
            for product_id, quantity in requested.items():
                product = self.store.get(Product, product_id)
                if product is None:
                    raise ProductNotFoundError(f"Product not found with id {product_id}")
                inventory = self.store.inventory_of(product_id)
                if inventory is None or inventory.quantity < quantity:
                    raise OutOfStockError(f"Quantity not available for product {product_id}")
                lines.append((product, inventory, quantity))

            order = self.store.add(Order(user=user))
            for product, inventory, quantity in lines:
                self.store.add(OrderItem(order=order, product=product, quantity=quantity))
                inventory.quantity -= quantity
            return order
