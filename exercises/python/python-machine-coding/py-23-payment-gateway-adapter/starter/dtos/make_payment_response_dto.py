from typing import Optional
from dtos.response_status import ResponseStatus
from models.payment_status import PaymentStatus


class MakePaymentResponseDto:
    """
    The output object returned from the makePayment functionality.

    Attributes:
        response_status : SUCCESS if the whole operation worked, FAILURE if anything went wrong
        txn_id          : the unique transaction ID from the payment gateway (None on failure)
        payment_status  : SUCCESS/FAILURE result from the gateway itself (None on failure)
    """

    def __init__(
        self,
        response_status: ResponseStatus,
        txn_id: Optional[str] = None,
        payment_status: Optional[PaymentStatus] = None,
    ):
        self.response_status = response_status
        self.txn_id = txn_id
        self.payment_status = payment_status
