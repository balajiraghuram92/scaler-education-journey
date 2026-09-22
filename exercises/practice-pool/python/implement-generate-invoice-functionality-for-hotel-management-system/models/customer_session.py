from typing import Optional

from .base_model import BaseModel
from .user import User
from .customer_session_status import CustomerSessionStatus


class CustomerSession(BaseModel):
    user: User
    customer_session_status: CustomerSessionStatus

    def __init__(
            self,
            user: User,
            customer_session_status,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.user = user
        self.customer_session_status = customer_session_status

