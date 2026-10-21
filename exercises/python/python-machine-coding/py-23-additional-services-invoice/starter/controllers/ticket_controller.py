from dtos.generate_ticket_request_dto import GenerateTicketRequestDto
from dtos.generate_ticket_response_dto import GenerateTicketResponseDto
from dtos.response_status import ResponseStatus
from services.ticket_service import TicketService


class TicketController:
    """
    Controller responsible for handling ticket generation requests.
    """

    def __init__(self, ticket_service: TicketService):
        self.ticket_service = ticket_service

    def generate_ticket(self, request_dto: GenerateTicketRequestDto) -> GenerateTicketResponseDto:
        """
        Generates a new parking ticket with optional additional services.
        """
        response_dto = GenerateTicketResponseDto()
        try:
            ticket = self.ticket_service.generate_ticket(
                request_dto.gate_id,
                request_dto.registration_number,
                request_dto.vehicle_type,
                request_dto.additional_services
            )
            response_dto.ticket = ticket
            response_dto.response_status = ResponseStatus.SUCCESS
        except Exception:
            response_dto.ticket = None
            response_dto.response_status = ResponseStatus.FAILURE
        return response_dto
