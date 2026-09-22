from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from scaler.exceptions import NotFoundError
from scaler.models import Lecture, Learner, ScheduledLecture, BatchLearner, Batch
from scaler.services import LectureServiceImpl


class TestLectureService(TestCase):

    def setUp(self):
        self.lecture_service = LectureServiceImpl()
        self.generate_data()

    def test_watch_lecture_with_scheduled_lecture_id(self):
        learner = self.data["learner"]
        scheduled_lecture = self.data["scheduled_lecture"]

        learner_progress = self.lecture_service.access_lecture(
            learner_id=learner.pk,
            scheduled_lecture_id=scheduled_lecture.pk,
            lecture_link=None
        )

        self.assertEqual(learner_progress.learner, learner)
        self.assertEqual(learner_progress.scheduled_lecture, scheduled_lecture)

    def test_watch_lecture_with_lecture_link(self):
        learner = self.data["learner"]
        scheduled_lecture: ScheduledLecture = self.data["scheduled_lecture"]

        learner_progress = self.lecture_service.access_lecture(
            learner_id=learner.pk,
            scheduled_lecture_id=None,
            lecture_link=scheduled_lecture.lecture_link
        )

        self.assertEqual(learner_progress.learner, learner)
        self.assertEqual(learner_progress.scheduled_lecture, scheduled_lecture)

    def test_watch_lecture_twice(self):
        learner = self.data["learner"]
        scheduled_lecture: ScheduledLecture = self.data["scheduled_lecture"]

        learner_progress1 = self.lecture_service.access_lecture(
            learner_id=learner.pk,
            scheduled_lecture_id=None,
            lecture_link=scheduled_lecture.lecture_link
        )

        learner_progress2 = self.lecture_service.access_lecture(
            learner_id=learner.pk,
            scheduled_lecture_id=None,
            lecture_link=scheduled_lecture.lecture_link
        )

        self.assertEqual(learner_progress1.learner, learner_progress2.learner)
        self.assertEqual(learner_progress1.scheduled_lecture, learner_progress2.scheduled_lecture)

    def test_watch_lecture_with_invalid_lecture_link(self):
        learner = self.data["learner"]
        scheduled_lecture: ScheduledLecture = self.data["scheduled_lecture"]

        with self.assertRaises(NotFoundError):
            learner_progress = self.lecture_service.access_lecture(
                learner_id=learner.pk,
                scheduled_lecture_id=None,
                lecture_link="invalid_link"
            )

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
