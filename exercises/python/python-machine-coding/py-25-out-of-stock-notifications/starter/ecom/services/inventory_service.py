from abc import ABC, abstractmethod

from ecom.models import Inventory


class InventoryService(ABC):

    @abstractmethod
    def save_or_update_inventory(self, product_id: int, quantity: int) -> Inventory:
        pass
