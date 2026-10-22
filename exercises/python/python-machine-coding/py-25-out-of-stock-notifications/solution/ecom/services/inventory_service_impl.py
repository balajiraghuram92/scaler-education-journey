from ecom.exceptions import ProductNotFoundError
from ecom.models import Inventory, Notification, NotificationStatus, Product
from ecom.services.email_service import EmailService
from ecom.services.inventory_service import InventoryService
from ecom.store import Store


class InventoryServiceImpl(InventoryService):
    def __init__(self, store: Store, email_service: EmailService) -> None:
        self.store = store
        self.email_service = email_service

    def save_or_update_inventory(self, product_id: int, quantity: int) -> Inventory:
        product = self.store.get(Product, product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")

        inventory = self.store.inventory_of(product_id)
        if inventory is None:
            inventory = self.store.add(Inventory(product=product, quantity=quantity))
        else:
            inventory.quantity = quantity

        for notification in self.store.find(Notification, product=product, status=NotificationStatus.PENDING):
            self.email_service.notify_user(user=notification.user, product=product)
            notification.status = NotificationStatus.SENT
        return inventory
