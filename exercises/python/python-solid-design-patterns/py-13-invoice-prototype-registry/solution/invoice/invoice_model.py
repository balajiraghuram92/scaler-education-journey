from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from copy import deepcopy

from .cloneable import Cloneable


class InvoiceType(Enum):
    STANDARD = "standard"
    PRO_FORMA = "pro_forma"
    RECURRING = "recurring"


@dataclass
class Invoice(Cloneable["Invoice"]):
    invoice_id: int
    customer_name: str
    amount: float
    payment_method: str
    type_: InvoiceType
    
    def clone_object(self) -> Invoice:
        return deepcopy(self)
