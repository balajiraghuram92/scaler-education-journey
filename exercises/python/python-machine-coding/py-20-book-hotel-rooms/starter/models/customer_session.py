from models.base_model import BaseModel
from models.user import User
from models.customer_session_status import CustomerSessionStatus

class CustomerSession(BaseModel):
    def __init__(self):
        super().__init__()
        self.user: User = None
        self.customer_session_status: CustomerSessionStatus = None

    def is_active(self) -> bool:
        return self.customer_session_status == CustomerSessionStatus.ACTIVE
