from abc import ABC, abstractmethod
from typing import List

from scaler.models import BatchLearner


class BatchService(ABC):

    @abstractmethod
    def add_learner_to_batch(
            self,
            admin_id: int,
            learner_id: int,
            batch_id: int,
    ) -> BatchLearner:
        pass

    @abstractmethod
    def remove_learner_from_batch(
            self,
            admin_id: int,
            learner_id: int,
            batch_id: int,
    ) -> BatchLearner:
        pass
