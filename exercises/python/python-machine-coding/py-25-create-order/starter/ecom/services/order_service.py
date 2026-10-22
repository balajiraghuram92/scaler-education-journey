from abc import ABC, abstractmethod
from typing import List, Tuple

from ecom.models import Order


class OrderService(ABC):

    @abstractmethod
    def place_order(self, user_id: int, product_ids_with_quantity: List[Tuple[int, int]]) -> Order:
        pass
