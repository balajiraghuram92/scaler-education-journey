from abc import ABC, abstractmethod
from datetime import datetime
from models.vehicle_type import VehicleType


class PricingStrategy(ABC):
    """
    Abstract base class for calculating parking fees based on duration and vehicle type.
    """

    @abstractmethod
    def calculate_amount(self, entry_time: datetime, exit_time: datetime, vehicle_type: VehicleType) -> float:
        """
        Calculates the parking fee for the time interval [entry_time, exit_time].

        Parameters:
            entry_time (datetime): When the vehicle entered.
            exit_time (datetime): When the vehicle is exiting.
            vehicle_type (VehicleType): The type of vehicle (CAR, BIKE, etc.).

        Returns:
            float: Total calculated parking amount.
        """
        pass
