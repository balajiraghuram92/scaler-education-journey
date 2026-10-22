from ecom.exceptions import NotificationNotFoundError, ProductInStockError, ProductNotFoundError, UserNotFoundError
from ecom.models import Notification, NotificationStatus, Product, User
from ecom.services.notification_service import NotificationService
from ecom.store import Store

class NotificationServiceImpl(NotificationService):

    def __init__(self, store: Store) -> None:
        """Keep the store."""
        raise NotImplementedError('TODO: implement __init__')

    def register_user(self, user_id: int, product_id: int) -> Notification:
        """UserNotFoundError for an unknown user; ProductNotFoundError when the product has no inventory; ProductInStockError when quantity > 0. Create a PENDING Notification, or reset an existing one for the pair to PENDING, and return it."""
        raise NotImplementedError('TODO: implement register_user')

    def unregister_user(self, user_id: int, product_id: int) -> None:
        """Delete the notification of the user for the product, or raise NotificationNotFoundError."""
        raise NotImplementedError('TODO: implement unregister_user')
