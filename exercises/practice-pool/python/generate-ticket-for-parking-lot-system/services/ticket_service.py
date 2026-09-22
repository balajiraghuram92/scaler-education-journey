from abc import ABC, abstractmethod
from typing import List

from models import VehicleType, Ticket


class TicketService(ABC):

    @abstractmethod
    def generate_ticket(
            self,
            gate_id: int,
            number_plate: str,
            vehicle_type: VehicleType
    ) -> Ticket:
        pass
