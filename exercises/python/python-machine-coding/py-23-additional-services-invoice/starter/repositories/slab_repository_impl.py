from typing import List, Dict
from models.slab import Slab
from models.vehicle_type import VehicleType
from repositories.slab_repository import SlabRepository


class SlabRepositoryImpl(SlabRepository):
    """
    In-memory implementation of the SlabRepository.
    """

    def __init__(self):
        self._slabs: Dict[int, Slab] = {}
        self._current_id = 1

    def get_sorted_slabs_by_vehicle_type(self, vehicle_type: VehicleType) -> List[Slab]:
        matched = [slab for slab in self._slabs.values() if slab.vehicle_type == vehicle_type]
        return sorted(matched, key=lambda s: s.start_hour)

    def save(self, slab: Slab) -> Slab:
        if slab.id is None or slab.id == 0:
            slab.id = self._current_id
            self._current_id += 1
        self._slabs[slab.id] = slab
        return slab
