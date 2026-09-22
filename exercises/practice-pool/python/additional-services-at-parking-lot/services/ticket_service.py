from abc import ABC, abstractmethod
from typing import List

from models import VehicleType, Ticket, AdditionalService


class TicketService(ABC):

    @abstractmethod
    def generate_ticket(
            self,
            gate_id: int,
            number_plate: str,
            vehicle_type: VehicleType,
            additional_services: List[AdditionalService]
    ) -> Ticket:
        pass
