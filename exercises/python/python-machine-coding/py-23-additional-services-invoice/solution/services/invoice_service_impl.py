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

    def __init__(
        self,
        ticket_repository: TicketRepository,
        pricing_strategy_factory: PricingStrategyFactory,
        gate_repository: GateRepository,
        invoice_repository: InvoiceRepository
    ):
        self.ticket_repository = ticket_repository
        self.pricing_strategy_factory = pricing_strategy_factory
        self.gate_repository = gate_repository
        self.invoice_repository = invoice_repository

    def create_invoice(self, ticket_id: int, gate_id: int, exit_time: Optional[datetime] = None) -> Invoice:
        """
        Creates an invoice for the ticket at the exit gate:
          1. Looks up ticket (raises TicketNotFoundException if missing).
          2. Looks up exit gate (raises InvalidGateException if missing or not an EXIT gate).
          3. Computes parking fee via pricing strategy selected by exit_time.
          4. Adds fees for any opted additional services.
          5. Saves invoice and frees the parking spot.
        """
        # Step 1: Validate Ticket
        ticket = self.ticket_repository.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundException(f"Ticket with id {ticket_id} not found.")

        # Step 2: Validate Exit Gate
        gate = self.gate_repository.find_by_id(gate_id)
        if gate is None:
            raise InvalidGateException(f"Gate with id {gate_id} not found.")
        if gate.gate_type != GateType.EXIT:
            raise InvalidGateException("Vehicle trying to exit from non-exit gate")

        # Step 3: Determine Exit Time and Pricing Strategy
        exit_dt = exit_time if exit_time is not None else datetime.now()
        pricing_strategy = self.pricing_strategy_factory.get_pricing_strategy(exit_dt)

        # Step 4: Calculate Parking Fee
        parking_fee = pricing_strategy.calculate_amount(
            ticket.entry_time, exit_dt, ticket.vehicle.vehicle_type
        )

        # Step 5: Calculate Additional Services Fee
        services_fee = sum(svc.cost for svc in ticket.additional_services)
        total_amount = float(parking_fee + services_fee)

        # Step 6: Create and Save Invoice
        invoice = Invoice(
            ticket=ticket,
            gate=gate,
            parking_attendant=gate.parking_attendant,
            exit_time=exit_dt,
            amount=total_amount
        )
        saved_invoice = self.invoice_repository.save(invoice)

        # Step 7: Free the Parking Spot
        if ticket.parking_spot is not None:
            ticket.parking_spot.status = ParkingSpotStatus.AVAILABLE

        return saved_invoice
