from adapters.payment_gateway_adapter import PaymentGatewayAdapter
from libraries.paytm.paytm_api import PaytmApi
from models.payment import Payment
from models.payment_status import PaymentStatus

class PaytmPaymentGatewayAdapter(PaymentGatewayAdapter):
    """
    Adapts the Paytm library to our system's standard PaymentGatewayAdapter interface.

    The Paytm library calls its method 'make_payment()' and returns a PaytmPaymentResponse.
    This adapter's job is to:
      1. Call the Paytm API using its own method name and argument style
      2. Convert the Paytm-specific response into our system's standard Payment object

    This means the rest of our system (the service) never needs to know it's talking to Paytm.
    """

    def __init__(self):
        """Create the PaytmApi SDK object and keep it."""
        raise NotImplementedError('TODO: implement __init__')

    def make_payment(self, bill_id: int, amount: float) -> Payment:
        """Call PaytmApi.make_payment(bill_id, amount), convert its string payment_status to PaymentStatus and return Payment(txn_id, payment_status, bill_id)."""
        raise NotImplementedError('TODO: implement make_payment')
