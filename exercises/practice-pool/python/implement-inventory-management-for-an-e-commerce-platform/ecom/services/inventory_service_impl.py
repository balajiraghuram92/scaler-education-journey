from .inventory_service import InventoryService
from ecom.models import Inventory, Product
from ecom.models import User, UserType
from ecom.exceptions import UnauthorizedAccessError, ProductNotFoundError, UserNotFoundError


class InventoryServiceImpl(InventoryService):

    def create_or_update_inventory(
            self,
            user_id: int,
            product_id: int,
            quantity: int
    ) -> Inventory:

        user = User.objects.filter(pk=user_id).first()

        if user is None:
            raise UserNotFoundError("User not found")

        if user.user_type != UserType.ADMIN.value:
            raise UnauthorizedAccessError("Only admin can update inventory")

        product = Product.objects.filter(id=product_id).first()

        if product is None:
            raise ProductNotFoundError("Product not found")

        inventory = Inventory.objects.filter(
            product=product
        ).first()

        if inventory is None:
            inventory = Inventory(
                product=product,
                quantity=quantity
            )
        else:
            inventory.quantity = quantity

        inventory.save()
        return inventory

    def delete_inventory(self, user_id: int, product_id: int) -> None:

        user = User.objects.filter(pk=user_id).first()

        if user is None:
            raise UserNotFoundError("User not found")

        if user.user_type != UserType.ADMIN.value:
            raise UnauthorizedAccessError("Only admin can update inventory")

        inventory = Inventory.objects.filter(
            product=product_id
        ).first()

        if inventory is not None:
            inventory.delete()
