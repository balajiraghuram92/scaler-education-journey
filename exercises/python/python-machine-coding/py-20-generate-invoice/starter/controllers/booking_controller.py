from dtos.generate_invoice_request_dto import GenerateInvoiceRequestDto
from dtos.generate_invoice_response_dto import GenerateInvoiceResponseDto
from dtos.response_status import ResponseStatus
from services.booking_service import BookingService

class BookingController:

    def __init__(self, booking_service: BookingService):
        raise NotImplementedError('TODO: implement __init__')

    def generate_invoice(self, request_dto: GenerateInvoiceRequestDto) -> GenerateInvoiceResponseDto:
        """SUCCESS with the invoice, or FAILURE with invoice=None when the service raises."""
        raise NotImplementedError('TODO: implement generate_invoice')
