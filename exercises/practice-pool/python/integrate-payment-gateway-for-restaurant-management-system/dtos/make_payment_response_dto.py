from dataclasses import dataclass, field
from .response_status import ResponseStatus


@dataclass
class MakePaymentResponseDto:
    response_status: ResponseStatus = field(default=None)
    txn_id: str = field(default=None)
    payment_status: str = field(default=None)
