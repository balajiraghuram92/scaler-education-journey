from abc import ABC, abstractmethod
from typing import List

from models import VehicleType, Ticket, AdditionalService, Invoice


class InvoiceService(ABC):

    @abstractmethod
    def create_invoice(
            self,
            gate_id: int,
            ticket_id: int,
    ) -> Invoice:
        pass
