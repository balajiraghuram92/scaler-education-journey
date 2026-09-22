from django.test import TestCase

from food_delivery.models import Partner, Task, Location
from food_delivery.services import TaskServiceImpl
from food_delivery.strategies import AllotNearestPartnerStrategy
from food_delivery.exceptions import NotFoundError


class TaskServiceTest(TestCase):

    def setUp(self):
        self.allocation_strategy = AllotNearestPartnerStrategy()
        self.tasks_service = TaskServiceImpl(self.allocation_strategy)

        self.generate_data()

    def test_partners_tasks_mappings(self):
        partners = self.data["partners"]
        tasks = self.data["tasks"]

        partner_ids = [partner.id for partner in partners]
        task_ids = [task.id for task in tasks]

        mappings = self.tasks_service.match_partners_and_tasks(partner_ids, task_ids)

        self.assertEqual(len(mappings), 2)

    def test_invalid_partners(self):
        partner_ids = [1, 2, 3, 4]
        tasks = self.data["tasks"]
        task_ids = [task.id for task in tasks]

        with self.assertRaises(NotFoundError):
            self.tasks_service.match_partners_and_tasks(partner_ids, task_ids)

    def test_invalid_tasks(self):
        partners = self.data["partners"]
        partner_ids = [partner.id for partner in partners]
        task_ids = [1, 2, 3, 4]

        with self.assertRaises(NotFoundError):
            self.tasks_service.match_partners_and_tasks(partner_ids, task_ids)

    def generate_data(self):
        partner1 = Partner.objects.create(name="partner1",
                                          location=Location.objects.create(latitude=12.9715987, longitude=77.5945667))
        partner2 = Partner.objects.create(name="partner2",
                                          location=Location.objects.create(latitude=12.9715987, longitude=77.5945668))
        partner3 = Partner.objects.create(name="partner3",
                                          location=Location.objects.create(latitude=12.9715987, longitude=77.5945669))

        task1 = Task.objects.create(
            customer_id=1,
            location=Location.objects.create(latitude=12.9715987, longitude=77.5945666)
        )

        task2 = Task.objects.create(
            customer_id=1,
            location=Location.objects.create(latitude=12.9715987, longitude=77.5945666)
        )

        self.data = {
            "partners": [partner1, partner2, partner3],
            "tasks": [task1, task2]
        }
