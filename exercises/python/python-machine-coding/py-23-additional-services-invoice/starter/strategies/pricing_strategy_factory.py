from datetime import datetime
from repositories.slab_repository import SlabRepository
from strategies.pricing_strategy import PricingStrategy
from strategies.weekday_pricing_strategy import WeekdayPricingStrategy
from strategies.weekend_pricing_strategy import WeekendPricingStrategy


class PricingStrategyFactory:
    """
    Factory responsible for selecting the appropriate pricing strategy based on exit day/time.
    """

    def __init__(self, slab_repository: SlabRepository):
        self.slab_repository = slab_repository

    def get_pricing_strategy(self, exit_time: datetime) -> PricingStrategy:
        """
        Determines whether exit_time falls on a weekend or weekday:
        - In Python datetime, exit_time.weekday() returns:
            0: Monday, 1: Tuesday, 2: Wednesday, 3: Thursday, 4: Friday, 5: Saturday, 6: Sunday
        - If exit_time.weekday() in (5, 6):
            return WeekendPricingStrategy(self.slab_repository)
        - Otherwise (0 to 4):
            return WeekdayPricingStrategy()
        """
        if exit_time.weekday() in (5, 6):
            return WeekendPricingStrategy(self.slab_repository)
        return WeekdayPricingStrategy()
