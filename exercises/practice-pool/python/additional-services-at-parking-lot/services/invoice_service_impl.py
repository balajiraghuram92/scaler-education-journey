from exceptions import NotFoundError
from repositories import GateRepository, TicketRepository, InvoiceRepository
from strategies import PricingStrategyFactory
from .invoice_service import InvoiceService
from datetime import datetime

from models import Invoice, Gate


class InvoiceServiceImpl(InvoiceService):

    gate_repository: GateRepository
    ticket_repository: TicketRepository
    invoice_repository: InvoiceRepository

    def __init__(
            self,
            gate_repository: GateRepository,
            ticket_repository: TicketRepository,
            invoice_repository: InvoiceRepository
    ):
        self.gate_repository = gate_repository
        self.ticket_repository = ticket_repository
        self.invoice_repository = invoice_repository

    def create_invoice(
            self,
            gate_id: int,
            ticket_id: int,
    ) -> Invoice:
        exit_gate: Gate = self.gate_repository.find_by_id(gate_id)
        if exit_gate is None:
            raise NotFoundError("Invalid gate id")
        ticket = self.ticket_repository.find_by_id(ticket_id)
        if ticket is None:
            raise NotFoundError("Invalid ticket id")
        entry_time = ticket.entry_time
        exit_time = datetime.now()

        pricing_strategy = PricingStrategyFactory.get_pricing_strategy()
        amount = pricing_strategy.calculate(ticket, entry_time, exit_time)

        for additional_service in ticket.additional_services:
            vehicle_types, price = additional_service.value
            if ticket.vehicle.vehicle_type in vehicle_types:
                amount += price

        invoice = Invoice(
            ticket=ticket,
            coordinator=exit_gate.coordinator,
            exit_time=exit_time,
            amount=amount,
            gate=exit_gate
        )

        invoice = self.invoice_repository.create(invoice)

        return invoice
