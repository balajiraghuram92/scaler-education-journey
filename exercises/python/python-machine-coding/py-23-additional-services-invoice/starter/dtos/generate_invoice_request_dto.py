class GenerateInvoiceRequestDto:
    """
    Request DTO to generate an invoice upon vehicle exit.
    """

    def __init__(self, ticket_id: int, gate_id: int):
        self.ticket_id = ticket_id
        self.gate_id = gate_id
