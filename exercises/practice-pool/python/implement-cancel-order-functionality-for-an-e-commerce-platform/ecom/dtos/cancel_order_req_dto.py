from dataclasses import dataclass, field


@dataclass
class CancelOrderReqDto:
    user_id: int
    order_id: int
