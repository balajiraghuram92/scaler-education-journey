from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from scaler.controllers import LectureController
from scaler.models import Lecture, Learner, ScheduledLecture, BatchLearner, Batch
from scaler.services import LectureServiceImpl
from scaler.dtos import AccessLectureResDto, AccessLectureReqDto, ResponseStatus


class TestLectureController(TestCase):

    def setUp(self):
        self.lecture_service = LectureServiceImpl()
        self.lecture_controller = LectureController(
            lecture_service=self.lecture_service
        )
        self.generate_data()

    def test_watch_lecture_with_scheduled_lecture_id(self):
        learner = self.data["learner"]
        scheduled_lecture = self.data["scheduled_lecture"]

        response: AccessLectureResDto = self.lecture_controller.access_lecture(
            request_dto=AccessLectureReqDto(
                learner_id=learner.pk,
                scheduled_lecture_id=scheduled_lecture.pk,
                lecture_link=None
            )
        )

        self.assertEqual(response.response_status, ResponseStatus.SUCCESS)
        learner_progress = response.learner_progress
        self.assertEqual(learner_progress.learner, learner)
        self.assertEqual(learner_progress.scheduled_lecture, scheduled_lecture)

    def test_watch_lecture_with_lecture_link(self):
        learner = self.data["learner"]
        scheduled_lecture: ScheduledLecture = self.data["scheduled_lecture"]

        response: AccessLectureResDto = self.lecture_controller.access_lecture(
            request_dto=AccessLectureReqDto(
                learner_id=learner.pk,
                scheduled_lecture_id=None,
                lecture_link=scheduled_lecture.lecture_link
            )
        )

        self.assertEqual(response.response_status, ResponseStatus.SUCCESS)

        learner_progress = response.learner_progress

        self.assertEqual(learner_progress.learner, learner)
        self.assertEqual(learner_progress.scheduled_lecture, scheduled_lecture)

    def test_watch_lecture_twice(self):
        learner = self.data["learner"]
        scheduled_lecture: ScheduledLecture = self.data["scheduled_lecture"]

        response1: AccessLectureResDto = self.lecture_controller.access_lecture(
            request_dto=AccessLectureReqDto(
                learner_id=learner.pk,
                scheduled_lecture_id=None,
                lecture_link=scheduled_lecture.lecture_link
            )
        )

        response2: AccessLectureResDto = self.lecture_controller.access_lecture(
            request_dto=AccessLectureReqDto(
                learner_id=learner.pk,
                scheduled_lecture_id=None,
                lecture_link=scheduled_lecture.lecture_link
            )
        )

        self.assertEqual(response1.response_status, ResponseStatus.SUCCESS)
        self.assertEqual(response2.response_status, ResponseStatus.SUCCESS)

        learner_progress1 = response1.learner_progress
        learner_progress2 = response2.learner_progress

        self.assertEqual(learner_progress1.pk, learner_progress2.pk)
        self.assertEqual(learner_progress1.learner, learner_progress2.learner)
        self.assertEqual(learner_progress1.scheduled_lecture, learner_progress2.scheduled_lecture)

    def test_watch_lecture_with_invalid_lecture_link(self):
        learner = self.data["learner"]

        response: AccessLectureResDto = self.lecture_controller.access_lecture(
            request_dto=AccessLectureReqDto(
                learner_id=learner.pk,
                scheduled_lecture_id=None,
                lecture_link="invalid_link"
            )
        )

        self.assertEqual(response.response_status, ResponseStatus.FAILURE)

    def generate_data(self):
        learner = Learner.objects.create(
            name="Learner1",
            email="learner1@gmail.com",
            phone="1234567890"
        )

        batch = Batch.objects.create(
            name="Batch1"
        )

        lecture = Lecture.objects.create(
            name="Lecture1",
            description="Description1",
        )

        BatchLearner.objects.create(
            learner=learner,
            batch=batch,
            entry_date=timezone.now() - timedelta(days=1)
        )

        scheduled_lecture = ScheduledLecture.objects.create(
            lecture=lecture,
            batch=batch,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1)
        )

        self.data = {
            "batch": batch,
            "learner": learner,
            "lecture": lecture,
            "scheduled_lecture": scheduled_lecture
        }
