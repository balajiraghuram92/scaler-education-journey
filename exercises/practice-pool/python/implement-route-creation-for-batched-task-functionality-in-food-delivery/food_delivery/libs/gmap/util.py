from dataclasses import dataclass
from typing import List
import random


@dataclass
class GLocation:
    lat: float
    lng: float


def get_optimized_route(locations: List[GLocation]):
    random.shuffle(locations)
    return locations
