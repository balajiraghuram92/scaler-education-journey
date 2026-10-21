from datetime import datetime
from models.vehicle_type import VehicleType
from repositories.slab_repository import SlabRepository
from strategies.pricing_strategy import PricingStrategy
from utils.date_time_utils import DateTimeUtils


class WeekendPricingStrategy(PricingStrategy):
    """
    Calculates weekend parking fees using vehicle-specific slab rates:
    - Duration is rounded up to the nearest integer hour.
    - Slabs are retrieved from the SlabRepository sorted by start_hour.
    - Slabs with end_hour == -1 indicate no upper limit (open-ended).
    """

    def __init__(self, slab_repository: SlabRepository):
        self.slab_repository = slab_repository

    def calculate_amount(self, entry_time: datetime, exit_time: datetime, vehicle_type: VehicleType) -> float:
        """
        Calculates weekend parking fees based on slabs for the given vehicle type.
        """
        total_hours = DateTimeUtils.calculate_hours(entry_time, exit_time)
        if total_hours <= 0:
            return 0.0

        slabs = self.slab_repository.get_sorted_slabs_by_vehicle_type(vehicle_type)
        total_amount = 0.0

        for slab in slabs:
            # If the parked duration does not reach this slab's start hour, we are done
            if total_hours <= slab.start_hour:
                break

            # Calculate the number of hours that fall within this slab
            if slab.end_hour == -1 or total_hours < slab.end_hour:
                hours_in_slab = total_hours - slab.start_hour
            else:
                hours_in_slab = slab.end_hour - slab.start_hour

            total_amount += hours_in_slab * slab.price

            # If this slab is open-ended or vehicle exit falls within this slab, stop
            if slab.end_hour == -1 or total_hours <= slab.end_hour:
                break

        return float(total_amount)
