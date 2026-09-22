from abc import ABC, abstractmethod
from ecom.models import Inventory


class NotificationService(ABC):

    @abstractmethod
    def register_user(
            self,
            user_id: int,
            product_id: int
    ) -> Inventory:
        pass

    @abstractmethod
    def unregister_user(
            self,
            user_id: int,
            product_id: int
    ) -> Inventory:
        pass
