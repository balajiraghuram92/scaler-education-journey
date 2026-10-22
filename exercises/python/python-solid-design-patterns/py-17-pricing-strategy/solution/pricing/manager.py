from .model import RideDetails
from .strategies import PricingStrategy


class PricingManager:
    def __init__(self, pricing_strategy: PricingStrategy):
        self.pricing_strategy = pricing_strategy

    def calculate_price(self, ride_details: RideDetails) -> float:
        return self.pricing_strategy.calculate_price(ride_details)
