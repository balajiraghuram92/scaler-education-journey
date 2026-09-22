from dataclasses import dataclass


@dataclass
class UnregisterUserNotifyReqDto:
    user_id: int
    product_id: int
