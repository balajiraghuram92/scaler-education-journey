from abc import ABC, abstractmethod
from typing import List
from food_delivery.models import Location


class MapsAdapter(ABC):
    @abstractmethod
    def build_route(self, locations: List[Location]) -> List[Location]:
        pass
