from __future__ import annotations

from typing import Optional, Dict

from .invoice_model import Invoice, InvoiceType
from .registry import InvoicePrototypeRegistry


class InvoicePrototypeRegistryImpl(InvoicePrototypeRegistry):

    def __init__(self):
        self.prototypes: Dict[InvoiceType, Invoice] = {}

    def add_prototype(self, invoice: Invoice) -> None:
        self.prototypes[invoice.type_] = invoice

    def get_prototype(self, type_: InvoiceType) -> Optional[Invoice]:
        return self.prototypes.get(type_)

    def clone(self, type_: InvoiceType) -> Optional[Invoice]:
        return (
            self.prototypes[type_].clone_object() if type_ in self.prototypes else None
        )
