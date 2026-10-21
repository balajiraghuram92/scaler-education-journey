class GenerateTicketRequestDto:
    """
    Data Transfer Object representing a request to generate a parking ticket.
    """

    def __init__(self, gate_id: int, registration_number: str, vehicle_type: str):
        self.gate_id = gate_id
        self.registration_number = registration_number
        self.vehicle_type = vehicle_type
