from services.booking_service import BookingService
from dtos.generate_invoice_request_dto import GenerateInvoiceRequestDto
from dtos.generate_invoice_response_dto import GenerateInvoiceResponseDto
from dtos.response_status import ResponseStatus


class BookingController:
    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service

    def generate_invoice(self, request_dto: GenerateInvoiceRequestDto) -> GenerateInvoiceResponseDto:

        response_dto: GenerateInvoiceResponseDto = GenerateInvoiceResponseDto()

        try:
            invoice = self.booking_service.generate_invoice(
                user_id=request_dto.user_id
            )

            response_dto.response_status = ResponseStatus.SUCCESS
            response_dto.invoice = invoice

        except Exception as e:
            print(e)
            response_dto.response_status = ResponseStatus.FAILURE

        return response_dto
