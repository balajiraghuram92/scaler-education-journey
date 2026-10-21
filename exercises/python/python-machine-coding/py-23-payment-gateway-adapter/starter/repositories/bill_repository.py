from abc import ABC, abstractmethod
from typing import Optional

from models.bill import Bill


class BillRepository(ABC):
    @abstractmethod
    def save(self, bill: Bill) -> Bill:
        pass

    @abstractmethod
    def find_by_id(self, bill_id: int) -> Optional[Bill]:
        pass
