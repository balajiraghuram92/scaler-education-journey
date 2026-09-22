from dataclasses import dataclass, field
from typing import List


@dataclass
class BroadcastMessageReqDto:
    batch_id: int
    sender_id: int
    message: str
