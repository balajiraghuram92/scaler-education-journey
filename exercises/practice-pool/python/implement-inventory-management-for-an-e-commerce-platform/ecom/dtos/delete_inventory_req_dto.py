from dataclasses import dataclass, field


@dataclass
class DeleteInventoryReqDto:
    user_id: int
    product_id: int
