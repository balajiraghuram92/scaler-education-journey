from .razorplay_payment_response import RazorpayPaymentResponse
from uuid import uuid4
from datetime import datetime


class RazorpayApi:

    def make_payment(
            self,
            order_id: int,
            amount: float
    ):

        return RazorpayPaymentResponse(
            txn_amount=amount,
            order_id=str(order_id),
            payment_status="SUCCESS",
            transaction_id=uuid4().hex,
            txt_date=datetime.now()
        )
