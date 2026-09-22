from models import Payment
from .payment_gateway_adapter import PaymentGatewayAdapter
from libraries.razorpay import RazorpayApi, RazorpayPaymentResponse
from models import PaymentStatus


class RazorpayAdapter(PaymentGatewayAdapter):
    razorpay_api: RazorpayApi

    def __init__(self):
        self.razorpay_api = RazorpayApi()

    def make_payment(
            self,
            bill_id: int,
            amount: float
    ):

        response: RazorpayPaymentResponse = self.razorpay_api.make_payment(
            bill_id,
            amount
        )

        return Payment(
            txn_id=response.transaction_id,
            bill_id=bill_id,
            payment_status=PaymentStatus.PENDING
        )

