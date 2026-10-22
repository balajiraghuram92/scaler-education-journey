from ecom.exceptions import ProductNotFoundError, UnauthorizedAccessError, UserNotFoundError
from ecom.models import Inventory, Product, User, UserType
from ecom.services.inventory_service import InventoryService
from ecom.store import Store


class InventoryServiceImpl(InventoryService):
    def __init__(self, store: Store) -> None:
        self.store = store

    def _require_admin(self, user_id: int) -> User:
        user = self.store.get(User, user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        if user.user_type is not UserType.ADMIN:
            raise UnauthorizedAccessError("Only admin can update inventory")
        return user

    def create_or_update_inventory(self, user_id: int, product_id: int, quantity: int) -> Inventory:
        self._require_admin(user_id)
        product = self.store.get(Product, product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")
        inventory = self.store.inventory_of(product_id)
        if inventory is None:
            return self.store.add(Inventory(product=product, quantity=quantity))
        inventory.quantity = quantity
        return inventory

    def delete_inventory(self, user_id: int, product_id: int) -> None:
        self._require_admin(user_id)
        inventory = self.store.inventory_of(product_id)
        if inventory is not None:
            self.store.delete(inventory)
