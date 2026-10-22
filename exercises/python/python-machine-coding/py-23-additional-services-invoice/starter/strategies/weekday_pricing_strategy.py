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
        """Hours between entry and exit rounded up (use DateTimeUtils.calculate_hours) times 10.0, never negative."""
        raise NotImplementedError('TODO: implement calculate_amount')
