from abc import ABC, abstractmethod
from typing import List

from ecom.models import Product


class RecommendationService(ABC):

    @abstractmethod
    def get_recommendations(
            self,
            product_id: int,
    ) -> List[int]:
        pass

