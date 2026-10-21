from datetime import datetime
from typing import Optional
from exceptions.invalid_gate_exception import InvalidGateException
from exceptions.ticket_not_found_exception import TicketNotFoundException
from models.gate_type import GateType
from models.invoice import Invoice
from models.parking_spot_status import ParkingSpotStatus
from repositories.gate_repository import GateRepository
from repositories.invoice_repository import InvoiceRepository
from repositories.ticket_repository import TicketRepository
from services.invoice_service import InvoiceService
from strategies.pricing_strategy_factory import PricingStrategyFactory

class InvoiceServiceImpl(InvoiceService):
    """
    Concrete implementation of InvoiceService.
    Calculates parking fee + additional services fee and releases the parking spot.
    """

    def __init__(self, ticket_repository: TicketRepository, pricing_strategy_factory: PricingStrategyFactory, gate_repository: GateRepository, invoice_repository: InvoiceRepository):
        """Keep the ticket repository, pricing strategy factory, gate repository and invoice repository."""
        raise NotImplementedError('TODO: implement __init__')

    def create_invoice(self, ticket_id: int, gate_id: int, exit_time: Optional[datetime]=None) -> Invoice:
        """Ticket must exist (TicketNotFoundException); gate must exist and be an EXIT gate (InvalidGateException). exit_time defaults to now. Amount = pricing strategy for exit_time (from the factory) parking fee + sum of the ticket's service costs. Save the Invoice (with the gate attendant), set the ticket's spot back to AVAILABLE and return the invoice."""
        raise NotImplementedError('TODO: implement create_invoice')
