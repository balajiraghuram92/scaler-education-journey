from typing import List, Optional

from .base_model import BaseModel
from .bill import Bill


class Customer(BaseModel):
    name: str
    visit_counts: int
    bills: List[Bill]

    def __init__(self,
                 name: str,
                 visit_counts: int = 0,
                 id: Optional[int] = None
                 ):
        super().__init__(id)
        self.name = name
        self.visit_counts = visit_counts
        self.bills = []
