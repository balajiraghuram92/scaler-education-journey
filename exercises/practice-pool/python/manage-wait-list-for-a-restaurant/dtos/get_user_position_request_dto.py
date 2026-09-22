from dataclasses import dataclass


@dataclass
class GetUserPositionRequestDto:
    user_id: int
