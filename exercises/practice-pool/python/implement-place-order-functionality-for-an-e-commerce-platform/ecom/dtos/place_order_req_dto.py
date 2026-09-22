from dataclasses import dataclass, field


@dataclass
class PlaceOrderReqDto:
    user_id: int
    product_ids_with_quantity: list[tuple[int, int]] = field(default_factory=list)
