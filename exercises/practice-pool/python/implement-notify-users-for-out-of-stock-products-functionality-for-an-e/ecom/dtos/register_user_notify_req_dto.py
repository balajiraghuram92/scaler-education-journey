from dataclasses import dataclass


@dataclass
class RegisterUserNotifyReqDto:
    user_id: int
    product_id: int
