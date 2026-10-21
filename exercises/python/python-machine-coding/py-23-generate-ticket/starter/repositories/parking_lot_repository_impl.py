from typing import Dict, Optional
from models.parking_lot import ParkingLot
from repositories.parking_lot_repository import ParkingLotRepository


class ParkingLotRepositoryImpl(ParkingLotRepository):
    """
    In-memory implementation of ParkingLotRepository using a dictionary.
    """

    def __init__(self):
        self._parking_lots: Dict[int, ParkingLot] = {}
        self._items = self._parking_lots
        self._current_id: int = 1

    def get_parking_lot_by_gate_id(self, gate_id: int) -> Optional[ParkingLot]:
        """
        Finds the parking lot containing a gate with the specified gate_id.
        """
        for lot in self._parking_lots.values():
            if lot.gates:
                for gate in lot.gates:
                    if gate.id == gate_id:
                        return lot
        return None

    def get_parking_lot_by_id(self, id: int) -> Optional[ParkingLot]:
        """
        Retrieves a parking lot by its unique ID.
        """
        return self._parking_lots.get(id)

    def save(self, parking_lot: ParkingLot) -> ParkingLot:
        """
        Saves a parking lot, assigning an auto-incrementing ID if needed.
        """
        if parking_lot.id is None or parking_lot.id <= 0:
            parking_lot.id = self._current_id
            self._current_id += 1

        self._parking_lots[parking_lot.id] = parking_lot
        return parking_lot
