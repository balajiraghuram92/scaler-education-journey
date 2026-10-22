from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


class GateType(Enum):
    ENTRY = "entry"
    EXIT = "exit"


class SpotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    OUT_OF_SERVICE = "out_of_service"


class FloorStatus(Enum):
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"


class PaymentMode(Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


class PaymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ParkingSpot:
    number: int
    supported_vehicle_type: VehicleType
    status: SpotStatus = SpotStatus.AVAILABLE


@dataclass
class ParkingFloor:
    floor_number: int
    spots: list[ParkingSpot] = field(default_factory=list)
    status: FloorStatus = FloorStatus.OPERATIONAL


@dataclass
class Operator:
    name: str


@dataclass
class Gate:
    gate_id: int
    gate_type: GateType
    operator: Operator | None = None


@dataclass
class ParkingLot:
    name: str
    floors: list[ParkingFloor]
    gates: list[Gate]


@dataclass
class Vehicle:
    registration_number: str
    vehicle_type: VehicleType


@dataclass
class Ticket:
    ticket_id: int
    vehicle: Vehicle
    spot: ParkingSpot
    gate: Gate
    entry_time: datetime


@dataclass
class Bill:
    ticket: Ticket
    gate: Gate
    exit_time: datetime
    amount: float


@dataclass
class Payment:
    bill: Bill
    amount: float
    mode: PaymentMode
    status: PaymentStatus
    reference: str


import math
from abc import ABC, abstractmethod


class InvalidParkingLotConfigError(Exception):
    """The Builder refused to create a lot; the message lists every problem."""


class SpotAssignmentStrategy(ABC):
    @abstractmethod
    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None: ...


def _available(floor: ParkingFloor, vehicle_type: VehicleType) -> list[ParkingSpot]:
    return [s for s in floor.spots
            if s.status is SpotStatus.AVAILABLE and s.supported_vehicle_type is vehicle_type]


class NearestSpotStrategy(SpotAssignmentStrategy):
    """First available matching spot on the lowest operational floor."""

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        for floor in sorted(lot.floors, key=lambda f: f.floor_number):
            if floor.status is FloorStatus.OPERATIONAL:
                free = _available(floor, vehicle_type)
                if free:
                    return min(free, key=lambda s: s.number)
        return None


class LeastAvailableFloorStrategy(SpotAssignmentStrategy):
    """Fill the fullest floor first: fewest free spots for this type, ties to the lowest floor."""

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        candidates = [(len(free), f.floor_number, free) for f in lot.floors
                      if f.status is FloorStatus.OPERATIONAL and (free := _available(f, vehicle_type))]
        if not candidates:
            return None
        _, _, free = min(candidates, key=lambda c: (c[0], c[1]))
        return min(free, key=lambda s: s.number)


class FeeStrategy(ABC):
    @abstractmethod
    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float: ...


class HourlyFeeStrategy(FeeStrategy):
    """Rate per started hour, by vehicle type."""

    RATES = {VehicleType.BIKE: 10.0, VehicleType.CAR: 20.0, VehicleType.TRUCK: 50.0}

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        hours = max(1, math.ceil((exit_ - entry).total_seconds() / 3600))
        return hours * self.RATES[vehicle_type]


class ParkingLotBuilder:
    def __init__(self, name: str) -> None:
        self._name = name
        self._floors: list[ParkingFloor] = []
        self._gates: list[Gate] = []

    def add_floor(self, floor: ParkingFloor) -> ParkingLotBuilder:
        self._floors.append(floor)
        return self

    def add_gate(self, gate: Gate) -> ParkingLotBuilder:
        self._gates.append(gate)
        return self

    def build(self) -> ParkingLot:
        problems = []
        if not self._floors:
            problems.append("at least one floor is required")
        if len({f.floor_number for f in self._floors}) != len(self._floors):
            problems.append("floor numbers must be unique")
        for f in self._floors:
            if len({s.number for s in f.spots}) != len(f.spots):
                problems.append(f"floor {f.floor_number} has duplicate spot numbers")
        kinds = {g.gate_type for g in self._gates}
        if GateType.ENTRY not in kinds or GateType.EXIT not in kinds:
            problems.append("need at least one entry gate and one exit gate")
        if problems:
            raise InvalidParkingLotConfigError("; ".join(problems))
        return ParkingLot(self._name, self._floors, self._gates)
