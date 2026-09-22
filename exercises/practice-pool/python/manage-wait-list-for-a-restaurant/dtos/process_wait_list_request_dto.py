from dataclasses import dataclass


@dataclass
class ProcessWaitListRequestDto:
    user_id: int
    number_of_seats: int
