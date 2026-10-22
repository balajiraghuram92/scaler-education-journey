from typing import Optional
from dtos.response_status import ResponseStatus
from models.ticket import Ticket


class GenerateTicketResponseDto:
    """
    Data Transfer Object representing the result of a ticket generation request.
    """

    def __init__(self, ticket: Optional[Ticket] = None, response_status: Optional[ResponseStatus] = None):
        self.ticket = ticket
        self.response_status = response_status
