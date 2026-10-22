from enum import Enum
from dataclasses import dataclass

class PricingType(Enum):
    DISTANCE_BASED = 1
    TIME_BASED = 2
    SURGE = 3

@dataclass
class RideDetails:
    distance: float
    duration: float