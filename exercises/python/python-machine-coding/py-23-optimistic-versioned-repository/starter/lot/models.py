from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(kw_only=True, eq=False)
class BaseModel:
    """Identity and audit fields shared by every persisted entity."""

    id: int | None = None
    created_at: datetime | None = None
    last_modified_at: datetime | None = None


@dataclass(eq=False)
class Gate(BaseModel):
    name: str
    gate_type: GateType


@dataclass(eq=False)
class ParkingSpot(BaseModel):
    number: int
    supported_vehicle_types: frozenset[VehicleType]     # one big spot can take a bike, a car or a truck
    status: SpotStatus = SpotStatus.AVAILABLE


@dataclass(eq=False)
class Vehicle(BaseModel):
    number: str
    vehicle_type: VehicleType
    owner_name: str


@dataclass(eq=False)
class Ticket(BaseModel):
    ticket_number: str
    entry_time: datetime
    vehicle: Vehicle
    spot: ParkingSpot
    gate: Gate


class ParkingLotError(Exception):
    """Base class for every domain failure the controller translates."""


class InvalidGateError(ParkingLotError):
    pass


class ParkingFullError(ParkingLotError):
    pass
