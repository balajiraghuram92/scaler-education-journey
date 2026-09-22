from datetime import datetime

from . import Gate, Coordinator
from .base_model import BaseModel
from .ticket import Ticket


class Invoice(BaseModel):
    ticket: Ticket
    gate: Gate
    coordinator: Coordinator
    exit_time: datetime
    amount: float

    def __init__(
            self,
            ticket: Ticket,
            exit_time: datetime,
            amount: float,
            gate: Gate,
            coordinator: Coordinator,
            id: int = None
    ):
        super().__init__(id)
        self.ticket = ticket
        self.exit_time = exit_time
        self.amount = amount
        self.gate = gate
        self.coordinator = coordinator
