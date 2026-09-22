from services import TicketService
from dtos import GenerateTicketRequestDto
from dtos import GenerateTicketResponseDto
from dtos import ResponseStatus



class TicketController:

    ticket_service: TicketService

    def __init__(self, ticket_service: TicketService):
        self.ticket_service = ticket_service

    def generate_ticket(self, request: GenerateTicketRequestDto):

        try:
            ticket = self.ticket_service.generate_ticket(
                gate_id=request.gate_id,
                number_plate=request.number_plate,
                vehicle_type=request.vehicle_type
            )
            return GenerateTicketResponseDto(
                response_status=ResponseStatus.SUCCESS,
                ticket=ticket
            )
        except Exception as e:
            return GenerateTicketResponseDto(
                response_status=ResponseStatus.FAILURE,
                ticket=None
            )
