from typing import List

from .task_service import TaskService
from food_delivery.models import Partner, Task, PartnerTaskMapping
from food_delivery.exceptions import NotFoundError
from food_delivery.strategies import MatchPartnerTaskStrategy


class TaskServiceImpl(TaskService):
    match_partner_task_strategy: MatchPartnerTaskStrategy

    def __init__(
            self,
            match_partner_task_strategy: MatchPartnerTaskStrategy
    ):
        self.match_partner_task_strategy = match_partner_task_strategy

    def match_partners_and_tasks(
            self,
            partner_ids: List[int],
            task_ids: List[int]
    ) -> List[PartnerTaskMapping]:
        partners = Partner.objects.filter(id__in=partner_ids)

        if len(partners) != len(partner_ids):
            raise NotFoundError("Invalid partner_ids")

        tasks = Task.objects.filter(id__in=task_ids)

        if len(tasks) != len(task_ids):
            raise NotFoundError("Invalid task_ids")

        mappings = self.match_partner_task_strategy.match_partners_and_tasks(partners, tasks)

        partner_task_mappings = []
        for mapping in mappings:
            partner, task = mapping
            partner_task_mapping = PartnerTaskMapping(
                partner=partner,
                task=task
            )
            partner_task_mapping.save()
            partner_task_mappings.append(partner_task_mapping)

        return partner_task_mappings





