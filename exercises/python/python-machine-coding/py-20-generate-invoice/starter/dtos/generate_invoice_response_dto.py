from typing import Optional
from models.invoice import Invoice
from dtos.response_status import ResponseStatus

class GenerateInvoiceResponseDto:
    def __init__(self):
        self.response_status: ResponseStatus = None
        self.invoice: Optional[Invoice] = None
