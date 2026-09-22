from django.test import TestCase

from scaler.models import Lecture, Instructor, Batch, ScheduledLecture, Schedule
from scaler.services import LectureServiceImpl
from scaler.utils import generate_lecture_link
from datetime import datetime
from scaler.exceptions import InvalidInstructorError, InvalidBatchError, InvalidLectureError


class TestLectureService(TestCase):

    def setUp(self):
        self.lecture_service = LectureServiceImpl()
        self.generate_data()

    def test_schedule_lectures_success(self):
        instructor = self.data["instructor"][0]
        batch = self.data["batches"][0]
        lectures = self.data["lectures"]

        datetime_str = '04/03/24 07:00:00'

        start_time = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        end_time = start_time.replace(
            hour=9,
            minute=30,
        )

        ScheduledLecture.objects.create(
            lecture=lectures[0],
            batch=batch,
            instructor=instructor,
            start_time=start_time,
            end_time=end_time,
            link=generate_lecture_link()
        )
        scheduled_lectures = self.lecture_service.schedule_lectures(
            batch_id=batch.pk,
            instructor_id=instructor.pk,
            lecture_ids=[lecture.pk for lecture in lectures[1:]]
        )

        assert len(scheduled_lectures) == len(lectures[1:]), "Scheduled lectures count is not equal to lectures count"

    def test_schedule_lectures_invalid_instructor(self):
        instructor = self.data["instructor"][0]
        batch = self.data["batches"][0]
        lectures = self.data["lectures"]

        datetime_str = '04/03/24 07:00:00'

        start_time = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        end_time = start_time.replace(
            hour=9,
            minute=30,
        )

        ScheduledLecture.objects.create(
            lecture=lectures[0],
            batch=batch,
            instructor=instructor,
            start_time=start_time,
            end_time=end_time,
            link=generate_lecture_link()
        )

        with self.assertRaises(InvalidInstructorError):

            scheduled_lectures = self.lecture_service.schedule_lectures(
                batch_id=batch.pk,
                instructor_id=100,
                lecture_ids=[lecture.pk for lecture in lectures[1:]]
            )

    def test_schedule_lectures_invalid_batch(self):
        instructor = self.data["instructor"][0]
        batch = self.data["batches"][0]
        lectures = self.data["lectures"]

        datetime_str = '04/03/24 07:00:00'

        start_time = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        end_time = start_time.replace(
            hour=9,
            minute=30,
        )

        ScheduledLecture.objects.create(
            lecture=lectures[0],
            batch=batch,
            instructor=instructor,
            start_time=start_time,
            end_time=end_time,
            link=generate_lecture_link()
        )

        with self.assertRaises(InvalidBatchError):

            scheduled_lectures = self.lecture_service.schedule_lectures(
                batch_id=100,
                instructor_id=instructor.pk,
                lecture_ids=[lecture.pk for lecture in lectures[1:]]
            )

    def generate_data(self):

        instructor1 = Instructor.objects.create(
            name="Instructor1",
            email="inst1@gmail.com"
        )

        batch1 = Batch.objects.create(
            name="Batch1",
            schedule=Schedule.MWF_MORNING
        )

        lectures = []
        for i in range(5):
            lecture = Lecture.objects.create(
                name="Lecture" + str(i),
                description="Description" + str(i)
            )
            lectures.append(lecture)

        self.data = {
            "instructor": [instructor1],
            "batches": [batch1],
            "lectures": lectures
        }



