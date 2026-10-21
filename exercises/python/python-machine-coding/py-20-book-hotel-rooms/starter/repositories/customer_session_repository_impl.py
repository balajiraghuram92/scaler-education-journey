from typing import Optional
from models.customer_session import CustomerSession
from models.customer_session_status import CustomerSessionStatus
from repositories.customer_session_repository import CustomerSessionRepository

class CustomerSessionRepositoryImpl(CustomerSessionRepository):

    def __init__(self):
        raise NotImplementedError('TODO: implement __init__')

    def save(self, customer_session: CustomerSession) -> CustomerSession:
        """Assign the next id when the id is 0, store the session and return it."""
        raise NotImplementedError('TODO: implement save')

    def find_active_customer_session_by_user_id(self, user_id: int) -> Optional[CustomerSession]:
        """The ACTIVE session of this user, or None."""
        raise NotImplementedError('TODO: implement find_active_customer_session_by_user_id')
