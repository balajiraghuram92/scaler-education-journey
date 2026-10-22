from typing import Dict, Optional

from .invoice_model import Invoice, InvoiceType
from .registry import InvoicePrototypeRegistry


class InvoicePrototypeRegistryImpl(InvoicePrototypeRegistry):
    """Keeps one prototype invoice per InvoiceType and hands out clones."""

    def __init__(self):
        self.prototypes: Dict[InvoiceType, Invoice] = {}

    def add_prototype(self, invoice: Invoice) -> None:
        """Store the invoice keyed by its ``type_`` (a second one of the same type replaces it)."""
        raise NotImplementedError("Implement add_prototype")

    def get_prototype(self, type_: InvoiceType) -> Optional[Invoice]:
        """Return the stored prototype itself, or None if there is none."""
        raise NotImplementedError("Implement get_prototype")

    def clone(self, type_: InvoiceType) -> Optional[Invoice]:
        """Return a CLONE of the stored prototype, or None for an unknown type."""
        raise NotImplementedError("Implement clone")
