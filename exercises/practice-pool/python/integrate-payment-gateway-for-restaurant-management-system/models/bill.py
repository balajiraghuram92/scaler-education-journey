from typing import Optional
from .base_model import BaseModel


class Bill(BaseModel):
    total_amount: int
    gst: int
    service_charge: int

    def __init__(
            self,
            total_amount: int,
            gst: int,
            service_charge: int,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.total_amount = total_amount
        self.service_charge = service_charge
        self.gst = gst


