from ecom.exceptions import (
    NotificationNotFoundError,
    ProductInStockError,
    ProductNotFoundError,
    UserNotFoundError,
)
from ecom.models import Notification, NotificationStatus, Product, User
from ecom.services.notification_service import NotificationService
from ecom.store import Store


class NotificationServiceImpl(NotificationService):
    def __init__(self, store: Store) -> None:
        self.store = store

    def register_user(self, user_id: int, product_id: int) -> Notification:
        user = self.store.get(User, user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} not found")

        inventory = self.store.inventory_of(product_id)
        if inventory is None:
            raise ProductNotFoundError(f"Product with id {product_id} is not listed in inventory")
        if inventory.quantity > 0:
            raise ProductInStockError(f"Product with id {product_id} is in stock")

        notification = self.store.first(Notification, user=user, product=inventory.product)
        if notification is None:
            return self.store.add(Notification(user=user, product=inventory.product))
        notification.status = NotificationStatus.PENDING
        return notification

    def unregister_user(self, user_id: int, product_id: int) -> None:
        user = self.store.get(User, user_id)
        product = self.store.get(Product, product_id)
        notification = None
        if user is not None and product is not None:
            notification = self.store.first(Notification, user=user, product=product)
        if notification is None:
            raise NotificationNotFoundError(f"No notification for user {user_id} and product {product_id}")
        self.store.delete(notification)
