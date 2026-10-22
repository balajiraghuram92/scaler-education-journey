from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


def started_hours(entry: datetime, exit_: datetime) -> int:
    """Every started hour counts: 61 minutes is 2 hours. The minimum bill is one hour."""
    return max(1, math.ceil((exit_ - entry).total_seconds() / 3600))


class FeeStrategy(ABC):
    @abstractmethod
    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float: ...


class WeekdayFee(FeeStrategy):
    """A flat rate of 10 per started hour for every vehicle type."""

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        return 10.0 * started_hours(entry, exit_)


@dataclass(frozen=True)
class Slab:
    start_hour: int
    end_hour: int          # -1 means "no upper limit"
    price: float           # per hour inside this slab


class WeekendSlabFee(FeeStrategy):
    """Each hour is charged at the rate of the slab it falls in (a marginal, tax-bracket style tariff)."""

    def __init__(self, slabs: Mapping[VehicleType, Sequence[Slab]]) -> None:
        self._slabs = {t: sorted(s, key=lambda slab: slab.start_hour) for t, s in slabs.items()}

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        hours, total = started_hours(entry, exit_), 0.0
        for slab in self._slabs[vehicle_type]:
            if hours <= slab.start_hour:
                break
            upper = hours if slab.end_hour == -1 else min(hours, slab.end_hour)
            total += (upper - slab.start_hour) * slab.price
        return total


class FeeStrategyFactory:
    """The single place that knows weekends differ: Saturday and Sunday have weekday() 5 and 6."""

    def __init__(self, weekday: FeeStrategy, weekend: FeeStrategy) -> None:
        self._weekday, self._weekend = weekday, weekend

    def for_exit_time(self, exit_: datetime) -> FeeStrategy:
        return self._weekend if exit_.weekday() in (5, 6) else self._weekday


class HolidayFee(FeeStrategy):
    """Decorator: wrap any tariff and multiply it when the exit date is a holiday."""

    def __init__(self, inner: FeeStrategy, holidays: frozenset[date], multiplier: float = 1.5) -> None:
        self._inner, self._holidays, self._multiplier = inner, holidays, multiplier

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        base = self._inner.calculate(entry, exit_, vehicle_type)
        return base * self._multiplier if exit_.date() in self._holidays else base
