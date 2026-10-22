from ecom.exceptions import ProductNotFoundError
from ecom.models import Inventory, Notification, NotificationStatus, Product
from ecom.services.email_service import EmailService
from ecom.services.inventory_service import InventoryService
from ecom.store import Store

class InventoryServiceImpl(InventoryService):

    def __init__(self, store: Store, email_service: EmailService) -> None:
        """Keep the store and the email service."""
        raise NotImplementedError('TODO: implement __init__')

    def save_or_update_inventory(self, product_id: int, quantity: int) -> Inventory:
        """ProductNotFoundError for an unknown product. Create the inventory or set its quantity. Then for every PENDING notification of that product call email_service.notify_user(user=..., product=...) and mark the notification SENT. Return the inventory."""
        raise NotImplementedError('TODO: implement save_or_update_inventory')
