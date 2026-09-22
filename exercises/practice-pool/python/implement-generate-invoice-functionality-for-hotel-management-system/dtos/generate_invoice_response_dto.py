from dataclasses import dataclass, field
from models.invoice import Invoice
from .response_status import ResponseStatus


@dataclass
class GenerateInvoiceResponseDto:

    invoice: Invoice = field(default=None)
    response_status: ResponseStatus = field(default=None)

