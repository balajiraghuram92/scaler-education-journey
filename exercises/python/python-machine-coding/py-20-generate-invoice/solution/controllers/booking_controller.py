from dtos.generate_invoice_request_dto import GenerateInvoiceRequestDto
from dtos.generate_invoice_response_dto import GenerateInvoiceResponseDto
from dtos.response_status import ResponseStatus
from services.booking_service import BookingService

class BookingController:
    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service

    def generate_invoice(self, request_dto: GenerateInvoiceRequestDto) -> GenerateInvoiceResponseDto:
        response = GenerateInvoiceResponseDto()
        
        try:
            invoice = self.booking_service.generate_invoice(request_dto.user_id)
            response.invoice = invoice
            response.response_status = ResponseStatus.SUCCESS
        except Exception as e:
            response.response_status = ResponseStatus.FAILURE
            
        return response
