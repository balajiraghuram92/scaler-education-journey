from abc import ABC, abstractmethod
from typing import Optional

from ecom.models import Notification


class NotificationService(ABC):

    @abstractmethod
    def register_user(self, user_id: int, product_id: int) -> Notification:
        pass

    @abstractmethod
    def unregister_user(self, user_id: int, product_id: int) -> None:
        pass
