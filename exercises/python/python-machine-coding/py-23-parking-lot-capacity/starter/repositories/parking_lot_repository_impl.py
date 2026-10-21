from typing import Dict, Optional
from models.parking_lot import ParkingLot
from repositories.parking_lot_repository import ParkingLotRepository

class ParkingLotRepositoryImpl(ParkingLotRepository):
    """
    In-memory implementation of the ParkingLotRepository using a dictionary.
    """

    def __init__(self):
        """Keep lots in a dict keyed by id plus a counter that hands out ids 1, 2, 3..."""
        raise NotImplementedError('TODO: implement __init__')

    def save(self, parking_lot: ParkingLot) -> ParkingLot:
        """Assign the next id when parking_lot.id is None or <= 0, store the lot and return it."""
        raise NotImplementedError('TODO: implement save')

    def get_parking_lot_by_id(self, id: int) -> Optional[ParkingLot]:
        """The lot or None."""
        raise NotImplementedError('TODO: implement get_parking_lot_by_id')

    def get_parking_lot_by_gate_id(self, gate_id: int) -> Optional[ParkingLot]:
        """The lot that has a gate with this id, or None."""
        raise NotImplementedError('TODO: implement get_parking_lot_by_gate_id')
