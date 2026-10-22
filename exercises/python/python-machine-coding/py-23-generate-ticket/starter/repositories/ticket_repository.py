from abc import ABC, abstractmethod
from typing import List, Optional

from models.ticket import Ticket


class TicketRepository(ABC):
    @abstractmethod
    def save(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        pass
