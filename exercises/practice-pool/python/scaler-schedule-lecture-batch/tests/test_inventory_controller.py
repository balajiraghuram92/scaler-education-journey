from django.test import TestCase

from scaler.controllers.lecture_controller import LectureController
from scaler.dtos import ScheduleLectureReqDto, ScheduleLectureResDto, ResponseStatus
from scaler.models import Lecture, Instructor, Batch, ScheduledLecture, Schedule
from scaler.services import LectureServiceImpl
from scaler.utils import generate_lecture_link
from datetime import datetime
from scaler.exceptions import InvalidInstructorError, InvalidBatchError, InvalidLectureError


class TestOrderController(TestCase):

    def setUp(self):
        self.lecture_service = LectureServiceImpl()
        self.lecture_controller = LectureController(self.lecture_service)
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

        response: ScheduleLectureResDto = self.lecture_controller.schedule_lectures(
            ScheduleLectureReqDto(
                batch_id=batch.pk,
                instructor_id=instructor.pk,
                lecture_ids=[lecture.pk for lecture in lectures[1:]]
            )
        )

        assert len(response.scheduled_lectures) == len(lectures[1:]), ("Scheduled lectures count is not equal to "
                                                                       "lectures count")
        assert response.response_status == ResponseStatus.SUCCESS, "Response status is not SUCCESS"
        assert response.scheduled_lectures[0].batch == batch, "Batch is not equal to the scheduled batch"
        assert response.scheduled_lectures[0].instructor == instructor, "Instructor is not equal to the"\
                                                                        " scheduled instructor"

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

        response: ScheduleLectureResDto = self.lecture_controller.schedule_lectures(
            ScheduleLectureReqDto(
                batch_id=batch.pk,
                instructor_id=100,
                lecture_ids=[lecture.pk for lecture in lectures[1:]]
            )
        )

        assert response.response_status == ResponseStatus.FAILURE, "Response status is not FAILURE"

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

        response: ScheduleLectureResDto = self.lecture_controller.schedule_lectures(
            ScheduleLectureReqDto(
                batch_id=100,
                instructor_id=instructor.pk,
                lecture_ids=[lecture.pk for lecture in lectures[1:]]
            )
        )

        assert response.response_status == ResponseStatus.FAILURE, "Response status is not FAILURE"

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



