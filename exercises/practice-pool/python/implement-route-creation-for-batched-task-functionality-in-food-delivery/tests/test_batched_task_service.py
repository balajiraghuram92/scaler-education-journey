from typing import List

from django.test import TestCase

from food_delivery.models import Task, Location, BatchedTask
from food_delivery.services import BatchedTaskServiceImpl
from food_delivery.adapters import GMapsMapsAdapter
from food_delivery.exceptions import NotFoundError, EmptyBatchError


class BatchedTaskServiceTest(TestCase):

    def setUp(self):
        self.maps_adapter = GMapsMapsAdapter()
        self.batched_tasks_service = BatchedTaskServiceImpl(self.maps_adapter)

        self.generate_data()

    def test_build_route(self):
        batched_tasks = self.data["batched_tasks"]

        # batch1 has 3 tasks
        batch = batched_tasks[0]
        route: List[Location] = self.batched_tasks_service.build_route(
            batch.id
        )

        self.assertEqual(len(route), len(batch.tasks.all()))

    def test_build_route_empty_batch(self):
        batched_tasks = self.data["batched_tasks"]

        # batch1 has 3 tasks
        batch = batched_tasks[2]

        with self.assertRaises(EmptyBatchError):
            route: List[Location] = self.batched_tasks_service.build_route(
                batch.id
            )

    def test_build_route_not_found(self):
        with self.assertRaises(NotFoundError):
            route: List[Location] = self.batched_tasks_service.build_route(
                123
            )

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
