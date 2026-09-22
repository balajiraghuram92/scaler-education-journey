from dataclasses import dataclass


@dataclass
class AddUserToWaitListRequestDto:
    user_id: int
