from .paytm_payment_response import PaytmPaymentResponse
from uuid import uuid4
from datetime import datetime


class PaytmApi:

    def make_payment(
            self,
            order_id: int,
            amount: float
    ):

        return PaytmPaymentResponse(
            txn_amount=amount,
            order_id=str(order_id),
            payment_status="SUCCESS",
            txn_id=uuid4().hex,
            txt_date=datetime.now()
        )