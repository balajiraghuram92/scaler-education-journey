from abc import ABC, abstractmethod

from models.ticket import Ticket


class TicketService(ABC):
    @abstractmethod
    def generate_ticket(self, gate_id, registration_number, vehicle_type, additional_services=None) -> Ticket:
        pass
