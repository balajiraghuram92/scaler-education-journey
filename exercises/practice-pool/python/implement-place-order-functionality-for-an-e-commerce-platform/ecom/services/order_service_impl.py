from typing import List, Tuple

from .order_service import OrderService
from django.db.transaction import atomic
from ecom.models import User, Order, OrderItem, Product, Inventory
from ecom.exceptions import UserNotFoundError, OutOfStockError, ProductNotFoundError


class OrderServiceImpl(OrderService):
    @atomic
    def place_order(
            self,
            user_id: int,
            product_ids_with_quantity: List[Tuple[int, int]]
    ) -> Order:

        user = User.objects.filter(pk=user_id).first()

        if user is None:
            raise UserNotFoundError("User not found")

        product_inventory_quantity = []

        # check if quantity is available for all products
        for product_id, quantity in product_ids_with_quantity:
            product = Product.objects.filter(pk=product_id).first()

            if product is None:
                raise ProductNotFoundError(f"Product not found with id {product_id}")

            inventory = Inventory.objects.filter(product=product).first()

            if inventory.quantity < quantity:
                raise OutOfStockError(f"Quantity not available for product {product_id}")

            product_inventory_quantity.append((product, inventory, quantity))

        order = Order.objects.create(
            user=user
        )

        for product, inventory, quantity in product_inventory_quantity:
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )
            inventory.quantity -= quantity
            inventory.save()

        return order
