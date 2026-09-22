from .notification_service import NotificationService
from ecom.models import Inventory, User, Notification, NotificationStatus
from ecom.exceptions import UserNotFoundError, ProductNotFoundError
from ecom.exceptions import NotificationNotFoundError, ProductInStockError


class NotificationServiceImpl(NotificationService):

    def register_user(
            self,
            user_id: int,
            product_id: int
    ) -> Notification:

        user: User = User.objects.filter(pk=user_id).first()
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} not found")

        inventory: Inventory = Inventory.objects.filter(product_id=product_id).first()

        if inventory is None:
            raise ProductNotFoundError(f"Product with id {product_id} is not listed in inventory")

        if inventory.quantity > 0:
            raise ProductInStockError(f"Product with id {product_id} is in stock")

        notification: Notification = Notification.objects.filter(user_id=user_id, product_id=product_id).first()

        if notification is None:
            notification = Notification.objects.create(
                user_id=user_id, product_id=product_id
            )
        else:
            notification.status = NotificationStatus.PENDING
            notification.save()
        return notification

    def unregister_user(
            self,
            user_id: int,
            product_id: int
    ) -> None:
        notification: Notification = Notification.objects.filter(
            user_id=user_id,
            product_id=product_id
        ).first()

        if notification is None:
            raise NotificationNotFoundError(
                f"""Notification for user with id {user_id} 
                and product with id {product_id} not found
                """)
        notification.delete()
