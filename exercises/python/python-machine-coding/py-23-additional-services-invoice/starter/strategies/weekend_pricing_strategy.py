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
        """Keep the slab repository."""
        raise NotImplementedError('TODO: implement __init__')

    def calculate_amount(self, entry_time: datetime, exit_time: datetime, vehicle_type: VehicleType) -> float:
        """Round the duration up to whole hours. Walk the vehicle type's slabs (sorted by start_hour) and add hours_in_slab x price for each slab the duration reaches; end_hour -1 means open-ended. 0 hours or no slabs: 0.0."""
        raise NotImplementedError('TODO: implement calculate_amount')
