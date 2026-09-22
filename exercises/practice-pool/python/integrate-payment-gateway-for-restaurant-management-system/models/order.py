from typing import Optional, Tuple
from .base_model import BaseModel
from .customer_session import CustomerSession
from .menu_item import MenuItem


class Order(BaseModel):
    customer_session: CustomerSession
    order_items: Tuple[MenuItem, int]

    def __init__(
            self,
            customer_session,
            order_items,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.customer_session = customer_session
        self.order_items = order_items
