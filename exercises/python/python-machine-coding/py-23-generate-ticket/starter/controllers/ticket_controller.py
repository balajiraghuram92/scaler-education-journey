from dtos.generate_ticket_request_dto import GenerateTicketRequestDto
from dtos.generate_ticket_response_dto import GenerateTicketResponseDto
from dtos.response_status import ResponseStatus
from exceptions.invalid_gate_exception import InvalidGateException
from exceptions.invalid_parking_lot_exception import InvalidParkingLotException
from exceptions.parking_spot_not_available_exception import ParkingSpotNotAvailableException
from services.ticket_service import TicketService

class TicketController:
    """
    The controller for handling ticket generation requests.
    """

    def __init__(self, ticket_service: TicketService):
        """Keep the ticket service."""
        raise NotImplementedError('TODO: implement __init__')

    def generate_ticket(self, request_dto: GenerateTicketRequestDto) -> GenerateTicketResponseDto:
        """SUCCESS with the ticket, or FAILURE with ticket=None for any failure."""
        raise NotImplementedError('TODO: implement generate_ticket')
