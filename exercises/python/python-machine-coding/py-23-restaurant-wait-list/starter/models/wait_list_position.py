from datetime import datetime
from models.base_model import BaseModel
from models.user import User


class WaitListPosition(BaseModel):
    """
    Represents one entry in the restaurant wait list.
    Each entry belongs to a specific User and records when they joined the wait list.

    The position of a customer in the wait list is determined by the order
    in which WaitListPosition entries were inserted (earliest inserted_at = position 1).
    """

    def __init__(self, user: User, inserted_at: datetime):
        super().__init__()
        self.user = user
        self.inserted_at = inserted_at
