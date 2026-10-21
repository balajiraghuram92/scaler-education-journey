from abc import ABC, abstractmethod

from ecom.models import Product, User


class EmailService(ABC):

    @abstractmethod
    def notify_user(self, user: User, product: Product) -> bool:
        pass
