from typing import Optional

from .base_model import BaseModel
from .payment_status import PaymentStatus


class Payment(BaseModel):
    txn_id: Optional[str]
    bill_id: Optional[str]
    payment_status: Optional[PaymentStatus]

    def __init__(
            self,
            txn_id: Optional[str],
            bill_id: Optional[int],
            payment_status: Optional[PaymentStatus] = PaymentStatus.PENDING,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.txn_id = txn_id
        self.payment_status = payment_status
        self.bill_id = bill_id
