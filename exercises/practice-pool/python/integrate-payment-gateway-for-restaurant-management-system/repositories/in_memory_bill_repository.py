from .bill_repository import BillRepository
from typing import Optional, Dict
from models import Bill


class InMemoryBillRepository(BillRepository):

    data: Dict[int, Bill]

    id_counter = 1

    def __init__(self):
        self.data = dict()

    def save(self, bill: Bill) -> Bill:
        if bill.id is None:
            bill.id = InMemoryBillRepository.id_counter
            InMemoryBillRepository.id_counter += 1

        self.data[bill.id] = bill
        return bill

    def find_by_id(self, bill_id) -> Optional[Bill]:

        if bill_id not in self.data:
            return None

        return self.data[bill_id]
