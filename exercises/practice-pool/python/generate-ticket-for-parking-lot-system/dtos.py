from dataclasses import dataclass
from enum import Enum
from typing import Optional

from models import VehicleType, Ticket


class ResponseStatus(Enum):
    SUCCESS = 1
    FAILURE = 2


@dataclass
class GenerateTicketRequestDto:
    gate_id: int
    number_plate: str
    vehicle_type: VehicleType


@dataclass
class GenerateTicketResponseDto:
    response_status: ResponseStatus
    ticket: Optional[Ticket]
