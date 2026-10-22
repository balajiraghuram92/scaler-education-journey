from adapters.payment_gateway_adapter import PaymentGatewayAdapter
from libraries.razorpay.razorpay_api import RazorpayApi
from models.payment import Payment
from models.payment_status import PaymentStatus

class RazorpayPaymentGatewayAdapter(PaymentGatewayAdapter):
    """
    Adapts the Razorpay library to our system's standard PaymentGatewayAdapter interface.

    Razorpay is different from Paytm in two important ways:
      1. Its method is called process_payment() instead of make_payment()
      2. Its transaction ID field is called transaction_id instead of txn_id

    This adapter hides those differences. Our service still just calls make_payment()
    on the adapter — it has no idea which gateway is actually being used underneath.
    """

    def __init__(self):
        """Create the RazorpayApi SDK object and keep it."""
        raise NotImplementedError('TODO: implement __init__')

    def make_payment(self, bill_id: int, amount: float) -> Payment:
        """Call RazorpayApi.process_payment(bill_id, amount), convert the string payment_status to PaymentStatus and return Payment(txn_id=response.transaction_id, payment_status, bill_id)."""
        raise NotImplementedError('TODO: implement make_payment')
