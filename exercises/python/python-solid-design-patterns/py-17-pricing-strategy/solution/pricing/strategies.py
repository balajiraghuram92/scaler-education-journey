from abc import ABC, abstractmethod

from .model import RideDetails

BASE_FARE = 5.0


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, ride_details: RideDetails) -> float:
        pass


class DistanceBasedPricingStrategy(PricingStrategy):
    PER_KILOMETER_RATE = 2.0

    def calculate_price(self, ride_details: RideDetails) -> float:
        return BASE_FARE + self.PER_KILOMETER_RATE * ride_details.distance


class TimeBasedPricingStrategy(PricingStrategy):
    PER_MINUTE_RATE = 0.5

    def calculate_price(self, ride_details: RideDetails) -> float:
        return BASE_FARE + self.PER_MINUTE_RATE * ride_details.duration


class SurgePricingStrategy(PricingStrategy):
    SURGE_MULTIPLIER = 2.0

    def calculate_price(self, ride_details: RideDetails) -> float:
        return BASE_FARE * self.SURGE_MULTIPLIER
