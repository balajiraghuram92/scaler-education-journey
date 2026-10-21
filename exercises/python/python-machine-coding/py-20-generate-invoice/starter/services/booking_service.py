from abc import ABC, abstractmethod
from models.invoice import Invoice

class BookingService(ABC):
    @abstractmethod
    def generate_invoice(self, user_id: int) -> Invoice:
        pass
