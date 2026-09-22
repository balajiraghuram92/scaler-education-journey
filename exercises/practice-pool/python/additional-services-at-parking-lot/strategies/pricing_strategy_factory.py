from models import VehicleType
from .pricing_strategy import PricingStrategy
from datetime import datetime


class WeekendPricingStrategy(PricingStrategy):

    def calculate_amount(
            self,
            exit_time: datetime,
            entry_time: datetime,
            vehicle_type: VehicleType,
    ):
        hours = (exit_time - entry_time).seconds // 3600
        minimum_amount = 50
        return min(minimum_amount, hours * 20)


class WeekdayPricingStrategy(PricingStrategy):

    def calculate_amount(
            self,
            exit_time: datetime,
            entry_time: datetime,
            vehicle_type: VehicleType,
    ):
        hours = (exit_time - entry_time).seconds // 3600
        minimum_amount = 30
        return min(minimum_amount, hours * 10)


class PricingStrategyFactory:

    @staticmethod
    def get_pricing_strategy():
        now = datetime.now()
        day = now.weekday()
        if day >= 5:
            return WeekendPricingStrategy()
        else:
            return WeekdayPricingStrategy()
