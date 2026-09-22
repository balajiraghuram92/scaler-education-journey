from dataclasses import dataclass


@dataclass
class MakePaymentRequestDto:
    bill_id: int
