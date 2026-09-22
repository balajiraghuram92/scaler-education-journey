from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaytmPaymentResponse:
    txn_id: str
    payment_status: str
    order_id: str
    txn_amount: float
    txt_date: datetime

