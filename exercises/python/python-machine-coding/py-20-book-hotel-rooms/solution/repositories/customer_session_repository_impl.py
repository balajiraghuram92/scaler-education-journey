from typing import Optional
from models.customer_session import CustomerSession
from models.customer_session_status import CustomerSessionStatus
from repositories.customer_session_repository import CustomerSessionRepository

class CustomerSessionRepositoryImpl(CustomerSessionRepository):
    def __init__(self):
        self.sessions = {}
        self.current_id = 1

    def save(self, customer_session: CustomerSession) -> CustomerSession:
        if customer_session.id == 0:
            customer_session.id = self.current_id
            self.current_id += 1
        self.sessions[customer_session.id] = customer_session
        return customer_session

    def find_active_customer_session_by_user_id(self, user_id: int) -> Optional[CustomerSession]:
        for session in self.sessions.values():
            if session.user.id == user_id and session.is_active():
                return session
        return None
