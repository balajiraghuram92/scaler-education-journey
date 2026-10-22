from dtos.generate_invoice_request_dto import GenerateInvoiceRequestDto
from dtos.generate_invoice_response_dto import GenerateInvoiceResponseDto
from dtos.response_status import ResponseStatus
from services.invoice_service import InvoiceService


class InvoiceController:
    """
    Controller responsible for handling invoice creation requests upon vehicle exit.
    """

    def __init__(self, invoice_service: InvoiceService):
        self.invoice_service = invoice_service

    def create_invoice(self, request_dto: GenerateInvoiceRequestDto) -> GenerateInvoiceResponseDto:
        """
        Creates an invoice for a parked vehicle when it exits the parking lot.
        """
        response_dto = GenerateInvoiceResponseDto()
        try:
            invoice = self.invoice_service.create_invoice(
                request_dto.ticket_id,
                request_dto.gate_id
            )
            response_dto.invoice = invoice
            response_dto.status = ResponseStatus.SUCCESS
        except Exception:
            response_dto.invoice = None
            response_dto.status = ResponseStatus.FAILURE
        return response_dto
