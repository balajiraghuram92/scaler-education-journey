from abc import ABC, abstractmethod
from datetime import timedelta


class MapAdapter(ABC):

    @abstractmethod
    def get_estimated_time(
        self, source_lat: float, source_long: float, destination_lat: float, destination_long: float
    ) -> timedelta:
        pass
