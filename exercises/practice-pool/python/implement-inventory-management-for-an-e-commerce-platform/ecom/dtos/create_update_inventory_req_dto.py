from dataclasses import dataclass, field


@dataclass
class CreateUpdateInventoryReqDto:
    user_id: int
    product_id: int
    quantity: int
