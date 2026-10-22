from typing import Dict

from models.invoice import Invoice
from repositories.invoice_repository import InvoiceRepository


class InvoiceRepositoryImpl(InvoiceRepository):
    """In-memory invoices keyed by id; ids start at 1."""

    def __init__(self):
        self._invoices: Dict[int, Invoice] = {}
        self._current_id: int = 1

    def save(self, invoice: Invoice) -> Invoice:
        if invoice.id is None or invoice.id <= 0:
            invoice.id = self._current_id
            self._current_id += 1
        self._invoices[invoice.id] = invoice
        return invoice
