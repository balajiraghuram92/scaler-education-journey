from dataclasses import dataclass, field
from typing import List


@dataclass
class FetchTimelineReqDto:
    learner_id: int
