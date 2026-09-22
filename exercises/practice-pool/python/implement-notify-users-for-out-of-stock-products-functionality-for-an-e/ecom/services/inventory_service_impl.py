from typing import Iterable

from .email_service import EmailService
from .inventory_service import InventoryService
from ecom.models import Inventory, Product, NotificationStatus, Notification
from ecom.exceptions import ProductNotFoundError


class InventoryServiceImpl(InventoryService):
    email_service: EmailService

    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def save_or_update_inventory(
            self,
            product_id: int,
            quantity: int
    ) -> Inventory:

        product = Product.objects.filter(id=product_id).first()

        if product is None:
            raise ProductNotFoundError("Product not found")

        inventory = Inventory.objects.filter(
            product=product
        ).first()

        if inventory is None:
            inventory = Inventory.objects.create(
                product=product,
                quantity=quantity
            )
        else:
            inventory.quantity = quantity
            inventory.save()

        notifications = Notification.objects.filter(
            product=product, status=NotificationStatus.PENDING
        ).all()

        print("Notifying", len(notifications))

        for notification in notifications:
            user_notified = self.email_service.notify_user(
                user=notification.user,
                product=product
            )

            notification.status = NotificationStatus.SENT
            notification.save()

        return inventory
