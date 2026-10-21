from typing import Optional
from dtos.response_status import ResponseStatus
from models.invoice import Invoice


class GenerateInvoiceResponseDto:
    """
    Response DTO containing the generated invoice and response status.
    """

    def __init__(self, invoice: Optional[Invoice] = None, status: Optional[ResponseStatus] = None):
        self.invoice = invoice
        self.status = status

    @property
    def response_status(self) -> Optional[ResponseStatus]:
        return self.status

    @response_status.setter
    def response_status(self, value: Optional[ResponseStatus]):
        self.status = value
