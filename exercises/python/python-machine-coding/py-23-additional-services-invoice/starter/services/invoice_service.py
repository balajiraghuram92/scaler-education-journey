from abc import ABC, abstractmethod

from models.invoice import Invoice


class InvoiceService(ABC):
    @abstractmethod
    def create_invoice(self, ticket_id: int, gate_id: int, exit_time=None) -> Invoice:
        pass
