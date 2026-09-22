from models import Payment
from .payment_gateway_adapter import PaymentGatewayAdapter
from libraries.paytm import PaytmApi, PaytmPaymentResponse
from models import PaymentStatus


class PaytmAdapter(PaymentGatewayAdapter):
    paytm_api: PaytmApi

    def __init__(self):
        self.paytm_api = PaytmApi()

    def make_payment(
            self,
            bill_id: int,
            amount: float
    ):

        response: PaytmPaymentResponse = self.paytm_api.make_payment(
            bill_id,
            amount
        )

        return Payment(
            txn_id=response.txn_id,
            bill_id=bill_id,
            payment_status=PaymentStatus.PENDING
        )
