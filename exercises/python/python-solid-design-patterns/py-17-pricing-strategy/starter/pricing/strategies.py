from abc import ABC, abstractmethod

from .model import RideDetails


class PricingStrategy(ABC):
    """Strategy interface.

    Declare one abstract method: calculate_price(self, ride_details: RideDetails) -> float
    """


class DistanceBasedPricingStrategy(PricingStrategy):
    """Base fare 5.0 plus 2.0 per kilometre (ride_details.distance)."""


class TimeBasedPricingStrategy(PricingStrategy):
    """Base fare 5.0 plus 0.5 per minute (ride_details.duration)."""


class SurgePricingStrategy(PricingStrategy):
    """Base fare 5.0 times a surge multiplier of 2.0 (ignores distance and duration)."""
