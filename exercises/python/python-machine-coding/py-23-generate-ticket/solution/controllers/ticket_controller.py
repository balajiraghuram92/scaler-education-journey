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
        self.ticket_service = ticket_service

    def generate_ticket(self, request_dto: GenerateTicketRequestDto) -> GenerateTicketResponseDto:
        """
        Processes a ticket generation request and returns the response DTO.
        """
        try:
            # Step 1: Validate request object and gate ID
            if request_dto is None:
                return GenerateTicketResponseDto(ticket=None, response_status=ResponseStatus.FAILURE)

            if request_dto.gate_id is None or request_dto.gate_id <= 0:
                return GenerateTicketResponseDto(ticket=None, response_status=ResponseStatus.FAILURE)

            # Step 2: Delegate ticket generation to the service
            ticket = self.ticket_service.generate_ticket(
                gate_id=request_dto.gate_id,
                registration_number=request_dto.registration_number,
                vehicle_type=request_dto.vehicle_type
            )

            # Step 3: Return SUCCESS response
            return GenerateTicketResponseDto(ticket=ticket, response_status=ResponseStatus.SUCCESS)

        except (InvalidGateException, InvalidParkingLotException, ParkingSpotNotAvailableException, Exception):
            # Step 4: Catch domain and general exceptions, returning a clean FAILURE response
            return GenerateTicketResponseDto(ticket=None, response_status=ResponseStatus.FAILURE)
