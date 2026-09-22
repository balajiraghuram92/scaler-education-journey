from abc import ABC, abstractmethod
from typing import Optional
from models import Bill


class BillRepository(ABC):

    @abstractmethod
    def save(self, bill: Bill) -> Bill:
        pass

    @abstractmethod
    def find_by_id(self, bill_id) -> Optional[Bill]:
        pass
