from dataclasses import dataclass, field
from typing import List


@dataclass
class ScheduleLectureReqDto:
    batch_id: int
    instructor_id: int
    lecture_ids: List[int]
