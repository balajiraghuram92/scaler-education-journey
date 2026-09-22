from typing import Optional

from .response_status import ResponseStatus
from dataclasses import dataclass

from scaler.models import BatchLearner


@dataclass
class AddLearnerToBatchReqDto:
    learner_id: int
    batch_id: int
    admin_id: int


@dataclass
class RemoveLearnerFromBatchReqDto:
    learner_id: int
    batch_id: int
    admin_id: int


@dataclass
class AddLearnerToBatchResDto:
    response_status: ResponseStatus
    batch_learner: Optional[BatchLearner]


@dataclass
class RemoveLearnerFromBatchResDto:
    response_status: ResponseStatus
    batch_learner: Optional[BatchLearner]
