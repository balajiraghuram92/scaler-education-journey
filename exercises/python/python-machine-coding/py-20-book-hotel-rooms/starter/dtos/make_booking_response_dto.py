from models.booking import Booking
from dtos.response_status import ResponseStatus

class MakeBookingResponseDto:
    def __init__(self):
        self.booking: Booking = None
        self.response_status: ResponseStatus = None
