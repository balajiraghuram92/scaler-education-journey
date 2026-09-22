from typing import List

from .batched_task_service import BatchedTaskService
from food_delivery.models import BatchedTask, Location
from food_delivery.exceptions import NotFoundError, EmptyBatchError
from food_delivery.adapters import MapsAdapter


class BatchedTaskServiceImpl(BatchedTaskService):
    maps_adapter: MapsAdapter

    def __init__(self, maps_adapter: MapsAdapter):
        self.maps_adapter = maps_adapter

    def build_route(self, batched_task_id: int) -> List[Location]:

        batched_task = BatchedTask.objects.filter(pk=batched_task_id).first()
        if not batched_task:
            raise NotFoundError('BatchedTask not found')

        tasks = batched_task.tasks.all()

        if len(tasks) == 0:
            raise EmptyBatchError('BatchedTask is empty')

        locations = [task.location for task in tasks]

        return self.maps_adapter.build_route(locations)
