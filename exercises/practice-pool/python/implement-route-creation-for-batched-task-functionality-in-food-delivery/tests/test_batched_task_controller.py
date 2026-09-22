from typing import List

from django.test import TestCase

from food_delivery.models import Task, Location, BatchedTask
from food_delivery.services import BatchedTaskServiceImpl
from food_delivery.controllers import BatchedTaskController
from food_delivery.adapters import GMapsMapsAdapter
from food_delivery.exceptions import NotFoundError, EmptyBatchError
from food_delivery.dtos import BuildBatchedTaskRouteRequestDto, BuildBatchedTaskRouteResponseDto
from food_delivery.dtos import ResponseStatus



class BatchedTaskControllerTest(TestCase):

    def setUp(self):
        self.maps_adapter = GMapsMapsAdapter()
        self.batched_tasks_service = BatchedTaskServiceImpl(self.maps_adapter)
        self.batched_tasks_controller = BatchedTaskController(self.batched_tasks_service)
        self.generate_data()

    def test_build_route(self):
        batched_tasks = self.data["batched_tasks"]

        # batch1 has 3 tasks
        batch = batched_tasks[0]
        response_dto : BuildBatchedTaskRouteResponseDto = self.batched_tasks_controller.build_route(
            BuildBatchedTaskRouteRequestDto(batched_task_id=batch.id)
        )
        route: List[Location] = response_dto.route_to_be_taken
        self.assertEqual(len(route), len(batch.tasks.all()))
        assert response_dto.response_status == ResponseStatus.SUCCESS

    def test_build_route_empty_batch(self):
        batched_tasks = self.data["batched_tasks"]

        # batch1 has 3 tasks
        batch = batched_tasks[2]

        response_dto: BuildBatchedTaskRouteResponseDto = self.batched_tasks_controller.build_route(
            BuildBatchedTaskRouteRequestDto(batched_task_id=batch.id)
        )

        assert response_dto.response_status == ResponseStatus.FAILURE

    def test_build_route_not_found(self):
        response_dto: BuildBatchedTaskRouteResponseDto = self.batched_tasks_controller.build_route(
            BuildBatchedTaskRouteRequestDto(batched_task_id=100)
        )
        assert response_dto.response_status == ResponseStatus.FAILURE

    def generate_data(self):

        # batch1 has 3 tasks
        # batch2 has 1 task
        # batch3 has no tasks

        task1 = Task.objects.create(
            location=Location.objects.create(latitude=12.9715987, longitude=77.5945666)
        )

        task2 = Task.objects.create(
            location=Location.objects.create(latitude=12.9715987, longitude=77.5945666)
        )

        task3 = Task.objects.create(
            location=Location.objects.create(latitude=12.9715987, longitude=77.5945666)
        )

        task4 = Task.objects.create(
            location=Location.objects.create(latitude=12.9715987, longitude=77.5945666)
        )

        batch1 = BatchedTask.objects.create()
        batch1.tasks.add(task1, task2, task3)

        batch2 = BatchedTask.objects.create()
        batch2.tasks.add(task4)

        batch3 = BatchedTask.objects.create()

        self.data = {
            "batched_tasks": [batch1, batch2, batch3],
        }
