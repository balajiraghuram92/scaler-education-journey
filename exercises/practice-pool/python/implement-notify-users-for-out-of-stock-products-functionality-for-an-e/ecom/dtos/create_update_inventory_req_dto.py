from dataclasses import dataclass


@dataclass
class CreateUpdateInventoryReqDto:
    user_id: int
    product_id: int
    quantity: int
