from typing import Dict, Optional
from models.ticket import Ticket
from repositories.ticket_repository import TicketRepository


class TicketRepositoryImpl(TicketRepository):
    """
    In-memory implementation of TicketRepository using a dictionary.
    """

    def __init__(self):
        self._tickets: Dict[int, Ticket] = {}
        self._items = self._tickets
        self._current_id: int = 1

    def save(self, ticket: Ticket) -> Ticket:
        """
        Saves a ticket, assigning an auto-incrementing ID if needed.
        """
        if ticket.id is None or ticket.id <= 0:
            ticket.id = self._current_id
            self._current_id += 1

        self._tickets[ticket.id] = ticket
        return ticket

    def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """
        Retrieves a ticket by its ID.
        """
        return self._tickets.get(ticket_id)
