from typing import Optional

from .base_model import BaseModel
from .dietary_requirement import DietaryRequirement
from .item_type import ItemType


class MenuItem(BaseModel):
    name: str
    price: float
    dietary_requirement: DietaryRequirement
    item_type: ItemType
    description: str

    def __init__(
            self,
            name: str,
            price: float,
            dietary_requirement: DietaryRequirement,
            item_type: ItemType,
            description: str = None,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.name = name
        self.price = price
        self.dietary_requirement = dietary_requirement
        self.item_type = item_type
        self.description = description
