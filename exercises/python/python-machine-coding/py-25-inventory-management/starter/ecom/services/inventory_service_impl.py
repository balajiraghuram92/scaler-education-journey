from ecom.exceptions import ProductNotFoundError, UnauthorizedAccessError, UserNotFoundError
from ecom.models import Inventory, Product, User, UserType
from ecom.services.inventory_service import InventoryService
from ecom.store import Store

class InventoryServiceImpl(InventoryService):

    def __init__(self, store: Store) -> None:
        """Keep the store."""
        raise NotImplementedError('TODO: implement __init__')

    def _require_admin(self, user_id: int) -> User:
        raise NotImplementedError('TODO: implement _require_admin')

    def create_or_update_inventory(self, user_id: int, product_id: int, quantity: int) -> Inventory:
        """UserNotFoundError for an unknown user, UnauthorizedAccessError unless the user is an ADMIN, ProductNotFoundError for an unknown product. Create the Inventory row, or replace the quantity of the existing one, and return it."""
        raise NotImplementedError('TODO: implement create_or_update_inventory')

    def delete_inventory(self, user_id: int, product_id: int) -> None:
        """Same user checks. Remove the product Inventory row if there is one; a missing row is not an error."""
        raise NotImplementedError('TODO: implement delete_inventory')
