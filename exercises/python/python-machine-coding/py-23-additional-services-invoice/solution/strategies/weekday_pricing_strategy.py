from datetime import datetime
from models.vehicle_type import VehicleType
from strategies.pricing_strategy import PricingStrategy
from utils.date_time_utils import DateTimeUtils


class WeekdayPricingStrategy(PricingStrategy):
    """
    Calculates weekday parking fees:
    - Fixed flat rate of Rs. 10 per hour across all vehicle types.
    - Duration in hours is rounded up to the nearest integer hour.
      (e.g., 1 hour 10 mins = 2 hours -> 2 * 10 = Rs. 20)
    """

    def calculate_amount(self, entry_time: datetime, exit_time: datetime, vehicle_type: VehicleType) -> float:
        """
        Calculates the parking fee for weekdays:
        1. Calculate duration in hours using DateTimeUtils.calculate_hours(entry_time, exit_time).
        2. Multiply hours by 10.0 and return the total fee as a float.
        """
        hours = DateTimeUtils.calculate_hours(entry_time, exit_time)
        return float(max(0, hours) * 10.0)
