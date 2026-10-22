from .model import RideDetails
from .strategies import PricingStrategy


class PricingManager:
    """Context that prices a ride with whichever PricingStrategy it is given.

    The old version branched on a PricingType enum and held the rate constants. Remove all
    of that: __init__ takes a strategy and stores it, and calculate_price(ride_details)
    simply delegates to it. The manager must not define BASE_FARE, PER_KILOMETER_RATE,
    PER_MINUTE_RATE or SURGE_MULTIPLIER.
    """

    def __init__(self, pricing_strategy: PricingStrategy):
        raise NotImplementedError("Store the strategy")

    def calculate_price(self, ride_details: RideDetails) -> float:
        raise NotImplementedError("Delegate to the strategy")
