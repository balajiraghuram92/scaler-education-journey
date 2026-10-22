from abc import ABC, abstractmethod
from typing import Optional

from .invoice_model import Invoice, InvoiceType


class InvoicePrototypeRegistry(ABC):

    @abstractmethod
    def add_prototype(self, invoice: Invoice) -> None:
        pass

    @abstractmethod
    def get_prototype(self, type_: InvoiceType) -> Optional[Invoice]:
        pass

    @abstractmethod
    def clone(self, type_: InvoiceType) -> Optional[Invoice]:
        pass
