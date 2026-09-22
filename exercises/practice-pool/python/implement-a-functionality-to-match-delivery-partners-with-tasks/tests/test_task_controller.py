from django.test import TestCase

from food_delivery.controllers import TaskController
from food_delivery.dtos import MatchPartnerTaskRequestDto
from food_delivery.dtos import ResponseStatus
from food_delivery.models import Partner, Task, Location
from food_delivery.services import TaskServiceImpl
from food_delivery.strategies import AllotNearestPartnerStrategy


class TaskControllerTest(TestCase):

    def setUp(self):
        self.allocation_strategy = AllotNearestPartnerStrategy()
        self.tasks_service = TaskServiceImpl(self.allocation_strategy)
        self.tasks_controller = TaskController(self.tasks_service)

        self.generate_data()

    def test_partners_tasks_mappings(self):
        partners = self.data["partners"]
        tasks = self.data["tasks"]

        partner_ids = [partner.id for partner in partners]
        task_ids = [task.id for task in tasks]

        response = self.tasks_controller.match_partners_and_tasks(
            request_dto=MatchPartnerTaskRequestDto(
                partner_ids=partner_ids,
                task_ids=task_ids
            )
        )

        mappings = response.partner_task_mappings

        assert response.response_status == ResponseStatus.SUCCESS
        self.assertEqual(len(mappings), 2)

    def test_invalid_partners(self):
        partner_ids = [1, 2, 3, 4]
        tasks = self.data["tasks"]
        task_ids = [task.id for task in tasks]
        response = self.tasks_controller.match_partners_and_tasks(
            request_dto=MatchPartnerTaskRequestDto(
                partner_ids=partner_ids,
                task_ids=task_ids
            )
        )

        assert response.response_status == ResponseStatus.FAILURE

    def test_invalid_tasks(self):
        partners = self.data["partners"]
        partner_ids = [partner.id for partner in partners]
        task_ids = [1, 2, 3, 4]
        response = self.tasks_controller.match_partners_and_tasks(
            request_dto=MatchPartnerTaskRequestDto(
                partner_ids=partner_ids,
                task_ids=task_ids
            )
        )

        assert response.response_status == ResponseStatus.FAILURE

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
