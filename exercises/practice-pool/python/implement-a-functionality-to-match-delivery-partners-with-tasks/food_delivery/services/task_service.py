from abc import ABC, abstractmethod
from typing import List

from food_delivery.models import PartnerTaskMapping


class TaskService(ABC):

    @abstractmethod
    def match_partners_and_tasks(
            self,
            partner_ids: List[int],
            task_ids: List[int]
    ) -> List[PartnerTaskMapping]:
        pass
