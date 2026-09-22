from typing import List, Optional
from .base_model import BaseModel
from .invoice import Invoice


class Customer(BaseModel):
    name: str
    invoices: List[Invoice]
    id: Optional[int]

    def __init__(
            self,
            name: str,
            invoices: List[Invoice] = None,
    ):
        super().__init__(id)
        self.name = name
        if invoices is None:
            invoices = []
        self.invoices = invoices




