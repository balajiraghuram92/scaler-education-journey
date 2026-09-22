from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from scaler.controllers import LearnerController
from scaler.models import Lecture, Learner, ScheduledLecture, BatchLearner, Batch
from scaler.services import LearnerServiceImpl
from scaler.dtos import FetchTimelineReqDto, FetchTimelineResDto, ResponseStatus


class TestLearnerController(TestCase):

    def setUp(self):

        self.learner_service = LearnerServiceImpl()
        self.learner_controller = LearnerController(learner_service=self.learner_service)
        self.generate_data()

    def test_success(self):

        learner = self.data["learners"][0]
        response: FetchTimelineResDto = self.learner_controller.fetch_timeline(
            request_dto=FetchTimelineReqDto(learner_id=learner.pk)
        )
        self.assertEqual(len(response.scheduled_lectures), 20)
        self.assertEqual(response.response_status, ResponseStatus.SUCCESS)

    def generate_data(self):

        learners = []

        for i in range(2):
            learner = Learner.objects.create(
                name="Learner" + str(i),
                email="learner" + str(i) + "@gmail.com",
                phone="1234567890"
            )
            learners.append(learner)

        batch1 = Batch.objects.create(
            name="Batch1"
        )

        batch2 = Batch.objects.create(
            name="Batch2"
        )

        lectures = []
        for i in range(20):
            lecture = Lecture.objects.create(
                name="Lecture" + str(i),
                description="Description" + str(i),
            )
            lectures.append(lecture)

        for lecture in lectures:
            ScheduledLecture.objects.create(
                lecture=lecture,
                batch=batch1,
                start_time=timezone.now() + timedelta(days=1)
            )

        for learner in learners:
            BatchLearner.objects.create(
                batch=batch1,
                learner=learner
            )

            BatchLearner.objects.create(
                batch=batch2,
                learner=learner
            )

        self.data = {
            "batches": [batch1, batch2],
            "learners": learners,
        }
