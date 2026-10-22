from abc import ABC, abstractmethod
from typing import Optional
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.vehicle_type import VehicleType


class SpotAssignmentStrategy(ABC):
    """
    Contract for assigning a parking spot to an incoming vehicle.
    """

    @abstractmethod
    def assign_spot(self, parking_lot: ParkingLot, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        """
        Assigns an available parking spot in the parking lot for the given vehicle type.

        Parameters:
            parking_lot (ParkingLot): The parking lot containing floors and spots.
            vehicle_type (VehicleType): The vehicle type to match (CAR, BIKE, etc.).

        Returns:
            Optional[ParkingSpot]: The assigned parking spot, or None if no spot is available.
        """
        pass
