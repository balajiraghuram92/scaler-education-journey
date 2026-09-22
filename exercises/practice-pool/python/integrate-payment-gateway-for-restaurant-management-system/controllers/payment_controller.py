from models import Payment
from services import PaymentService
from dtos import MakePaymentRequestDto
from dtos import MakePaymentResponseDto
from dtos import ResponseStatus


class PaymentController:
    payment_service: PaymentService

    def __init__(
            self,
            payment_service: PaymentService
    ):
        self.payment_service = payment_service

    def make_payment(
            self,
            request_dto: MakePaymentRequestDto
    ):

        try:
            payment: Payment = self.payment_service.make_payment(
                request_dto.bill_id
            )

            return MakePaymentResponseDto(
                txn_id = payment.txn_id,
                payment_status=payment.payment_status.name,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            return MakePaymentResponseDto(
                response_status=ResponseStatus.FAILURE
            )




