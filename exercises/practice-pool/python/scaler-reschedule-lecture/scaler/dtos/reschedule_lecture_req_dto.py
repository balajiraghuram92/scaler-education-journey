from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RescheduleLectureReqDto:
    scheduled_lecture_id: int
