from abc import ABC, abstractmethod
from ecom.models import Inventory


class InventoryService(ABC):

    @abstractmethod
    def create_or_update_inventory(
            self,
            user_id: int,
            product_id: int,
            quantity: int
    ) -> Inventory:
        pass

    @abstractmethod
    def delete_inventory(self, user_id: int, product_id: int) -> None:
        pass
