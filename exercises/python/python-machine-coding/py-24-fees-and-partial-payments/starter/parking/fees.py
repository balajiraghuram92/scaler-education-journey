from __future__ import annotations
import math
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

class VehicleType(Enum):
    BIKE = 'bike'
    CAR = 'car'
    TRUCK = 'truck'

def started_hours(entry: datetime, exit_: datetime) -> int:
    """Whole started hours between entry and exit (61 minutes is 2 hours), at least 1."""
    raise NotImplementedError('TODO: implement started_hours')

class FeeStrategy(ABC):

    @abstractmethod
    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        ...

class WeekdayFee(FeeStrategy):
    """A flat rate of 10 per started hour for every vehicle type."""

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        """10.0 per started hour for every vehicle type."""
        raise NotImplementedError('TODO: implement calculate')

@dataclass(frozen=True)
class Slab:
    start_hour: int
    end_hour: int
    price: float

class WeekendSlabFee(FeeStrategy):
    """Each hour is charged at the rate of the slab it falls in (a marginal, tax-bracket style tariff)."""

    def __init__(self, slabs: Mapping[VehicleType, Sequence[Slab]]) -> None:
        """Keep the slabs per vehicle type, sorted by start_hour."""
        raise NotImplementedError('TODO: implement __init__')

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        """Marginal pricing: each started hour is charged at the rate of the slab it falls in (end_hour -1 means no upper limit)."""
        raise NotImplementedError('TODO: implement calculate')

class FeeStrategyFactory:
    """The single place that knows weekends differ: Saturday and Sunday have weekday() 5 and 6."""

    def __init__(self, weekday: FeeStrategy, weekend: FeeStrategy) -> None:
        """Keep the weekday and weekend strategies."""
        raise NotImplementedError('TODO: implement __init__')

    def for_exit_time(self, exit_: datetime) -> FeeStrategy:
        """The weekend strategy when the exit is on a Saturday or Sunday, otherwise the weekday strategy."""
        raise NotImplementedError('TODO: implement for_exit_time')

class HolidayFee(FeeStrategy):
    """Decorator: wrap any tariff and multiply it when the exit date is a holiday."""

    def __init__(self, inner: FeeStrategy, holidays: frozenset[date], multiplier: float=1.5) -> None:
        """Keep the inner strategy, the set of holiday dates and the multiplier (default 1.5)."""
        raise NotImplementedError('TODO: implement __init__')

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        """The inner fee, multiplied when exit_.date() is a holiday."""
        raise NotImplementedError('TODO: implement calculate')
