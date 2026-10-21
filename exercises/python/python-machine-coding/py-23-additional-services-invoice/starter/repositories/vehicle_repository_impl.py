from typing import Dict, Optional
from models.vehicle import Vehicle
from repositories.vehicle_repository import VehicleRepository


class VehicleRepositoryImpl(VehicleRepository):
    """
    In-memory implementation of VehicleRepository using a dictionary.
    """

    def __init__(self):
        self._vehicles: Dict[int, Vehicle] = {}
        self._items = self._vehicles
        self._current_id: int = 1

    def get_vehicle_by_registration_number(self, registration_number: str) -> Optional[Vehicle]:
        """
        Finds a vehicle by its registration number.
        """
        for vehicle in self._vehicles.values():
            if vehicle.registration_number == registration_number:
                return vehicle
        return None

    def save(self, vehicle: Vehicle) -> Vehicle:
        """
        Saves a vehicle, assigning an auto-incrementing ID if needed.
        """
        if vehicle.id is None or vehicle.id <= 0:
            vehicle.id = self._current_id
            self._current_id += 1

        self._vehicles[vehicle.id] = vehicle
        return vehicle
