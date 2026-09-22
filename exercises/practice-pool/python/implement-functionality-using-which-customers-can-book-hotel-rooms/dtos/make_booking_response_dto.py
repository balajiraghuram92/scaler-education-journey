from dataclasses import dataclass, field
from models.booking import Booking
from .response_status import ResponseStatus


@dataclass
class MakeBookingResponseDto:
    booking: Booking = field(default=None)
    response_status: ResponseStatus = field(default=None)
