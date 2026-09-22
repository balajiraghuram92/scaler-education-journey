from abc import ABC, abstractmethod
from datetime import datetime


class ProductService(ABC):

    @abstractmethod
    def estimate_delivery_date(
            self,
            product_id: int,
            address_id: int
    ) -> datetime:
        pass
