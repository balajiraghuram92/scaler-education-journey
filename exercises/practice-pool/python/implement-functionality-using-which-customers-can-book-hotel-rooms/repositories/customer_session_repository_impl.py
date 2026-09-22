from typing import Dict, Optional

from models.customer_session import CustomerSession
from models.customer_session_status import CustomerSessionStatus
from .customer_session_repository import CustomerSessionRepository


class InMemoryCustomerSessionRepositoryImpl(CustomerSessionRepository):
    id_Counter = 0

    def __init__(self):
        self._rooms_dict: Dict[int, CustomerSession] = dict()

    def save(self, customer_session: CustomerSession) -> CustomerSession:
        if customer_session.id is None:
            customer_session.id = InMemoryCustomerSessionRepositoryImpl.id_Counter + 1
            InMemoryCustomerSessionRepositoryImpl.id_Counter += 1

        self._rooms_dict[customer_session.id] = customer_session
        return customer_session

    def find_active_customer_session_by_user_id(self, user_id: int) -> Optional[CustomerSession]:
        filtered = filter(lambda session: (session.user.id == user_id) and (session.status == CustomerSessionStatus.ACTIVE), self._rooms_dict.values())
        result = list(filtered)
        if len(result) == 0:
            return None
        else:
            return result[0]