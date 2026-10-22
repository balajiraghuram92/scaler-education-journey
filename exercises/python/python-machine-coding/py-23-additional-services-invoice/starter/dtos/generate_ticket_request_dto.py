from typing import List, Optional


class GenerateTicketRequestDto:
    """
    Request DTO to generate a ticket with optional additional services.
    """

    def __init__(
        self,
        gate_id: int,
        registration_number: str,
        vehicle_type: str,
        additional_services: Optional[List[str]] = None
    ):
        self.gate_id = gate_id
        self.registration_number = registration_number
        self.vehicle_type = vehicle_type
        self.additional_services = additional_services if additional_services is not None else []
