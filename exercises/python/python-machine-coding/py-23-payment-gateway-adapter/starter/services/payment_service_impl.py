from services.payment_service import PaymentService
from repositories.bill_repository import BillRepository
from adapters.payment_gateway_adapter import PaymentGatewayAdapter
from exceptions.invalid_bill_exception import InvalidBillException
from models.payment import Payment

class PaymentServiceImpl(PaymentService):
    """
    The concrete implementation of the PaymentService.

    This class contains the core business logic for processing a payment:
      1. Check that the bill actually exists in the system
      2. Get the total amount from the bill
      3. Send the payment to the gateway via the adapter
      4. Return the result

    Notice that this class depends on:
      - A BillRepository  (to fetch bill data)
      - A PaymentGatewayAdapter (to process the payment)

    Both of these are INTERFACES (abstract classes). This means we can swap out
    the implementation (e.g., switch from Paytm to Razorpay) without changing
    a single line of this service. This is Dependency Injection + the Open/Closed principle.
    """

    def __init__(self, bill_repository: BillRepository, payment_gateway_adapter: PaymentGatewayAdapter):
        """Keep the bill repository and the payment gateway adapter."""
        raise NotImplementedError('TODO: implement __init__')

    def make_payment(self, bill_id: int) -> Payment:
        """Find the bill (None raises InvalidBillException("Invalid bill id")), then ask the adapter to pay bill.get_amount_to_be_paid() and return its Payment."""
        raise NotImplementedError('TODO: implement make_payment')
