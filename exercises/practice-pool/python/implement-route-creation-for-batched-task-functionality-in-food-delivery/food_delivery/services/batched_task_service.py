from abc import ABC, abstractmethod
from typing import List

from food_delivery.models import Location


class BatchedTaskService(ABC):

    @abstractmethod
    def build_route(
            self,
            batched_task_id: int,
    ) -> List[Location]:
        pass
