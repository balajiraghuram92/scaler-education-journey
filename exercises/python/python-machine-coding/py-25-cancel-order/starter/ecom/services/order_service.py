from abc import ABC, abstractmethod

from ecom.models import Order


class OrderService(ABC):

    @abstractmethod
    def cancel_order(self, user_id: int, order_id: int) -> Order:
        pass
