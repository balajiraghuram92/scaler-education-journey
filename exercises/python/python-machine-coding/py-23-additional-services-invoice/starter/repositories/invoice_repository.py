from abc import ABC, abstractmethod
from typing import List, Optional

from models.invoice import Invoice


class InvoiceRepository(ABC):
    @abstractmethod
    def save(self, invoice: Invoice) -> Invoice:
        pass
