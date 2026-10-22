from dtos.make_payment_request_dto import MakePaymentRequestDto
from dtos.make_payment_response_dto import MakePaymentResponseDto
from dtos.response_status import ResponseStatus
from exceptions.invalid_bill_exception import InvalidBillException
from services.payment_service import PaymentService

class PaymentController:
    """
    The controller acts as the entry point for the make payment feature.
    It receives a request, delegates the work to the service, and returns a response.

    The controller itself does NOT contain any business logic — it only:
      1. Passes the request data to the service
      2. Catches exceptions from the service
      3. Wraps the result (or error) into a response DTO
    """

    def __init__(self, payment_service: PaymentService):
        """Keep the payment service."""
        raise NotImplementedError('TODO: implement __init__')

    def make_payment(self, request: MakePaymentRequestDto) -> MakePaymentResponseDto:
        """Return MakePaymentResponseDto(SUCCESS, txn_id, payment_status) on success. InvalidBillException becomes FAILURE with txn_id=None and payment_status=None. Do not catch anything else."""
        raise NotImplementedError('TODO: implement make_payment')
