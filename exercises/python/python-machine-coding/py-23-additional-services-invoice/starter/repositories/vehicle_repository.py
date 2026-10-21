from abc import ABC, abstractmethod
from typing import List, Optional

from models.vehicle import Vehicle


class VehicleRepository(ABC):
    @abstractmethod
    def get_vehicle_by_registration_number(self, registration_number: str) -> Optional[Vehicle]:
        pass

    @abstractmethod
    def save(self, vehicle: Vehicle) -> Vehicle:
        pass
