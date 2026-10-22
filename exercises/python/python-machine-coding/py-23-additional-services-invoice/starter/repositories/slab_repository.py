from abc import ABC, abstractmethod
from typing import List, Optional

from models.slab import Slab
from models.vehicle_type import VehicleType


class SlabRepository(ABC):
    @abstractmethod
    def get_sorted_slabs_by_vehicle_type(self, vehicle_type: VehicleType) -> List[Slab]:
        pass

    @abstractmethod
    def save(self, slab: Slab) -> Slab:
        pass
