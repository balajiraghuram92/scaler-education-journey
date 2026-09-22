from django.test import TestCase

from scaler.models import Lecture, Instructor, Batch, ScheduledLecture, Schedule
from scaler.services import LectureServiceImpl
from scaler.utils import generate_lecture_link
from datetime import datetime
from scaler.utils import get_future_schedule_dates
from scaler.controllers import LectureController
from scaler.dtos import RescheduleLectureReqDto, RescheduleLectureResDto, ResponseStatus


class TestLectureController(TestCase):

    def setUp(self):
        self.lecture_service = LectureServiceImpl()
        self.lecture_controller = LectureController(self.lecture_service)
        self.generate_data()

    def test_schedule_lectures_success(self):
        instructor = self.data["instructor"][0]
        batch = self.data["batches"][0]
        lectures = self.data["lectures"]

        datetime_str = '04/03/24 07:00:00'
        start_time = datetime.strptime(datetime_str, '%y/%m/%d %H:%M:%S')
        lecture_schedule_dates = get_future_schedule_dates(
            start_time,
            batch.schedule.value,
            len(lectures)
        )

        scheduled_lectures = []

        for (start_time, end_time), lecture in zip(lecture_schedule_dates, lectures):
            scheduled = ScheduledLecture.objects.create(
                lecture=lecture,
                batch=batch,
                instructor=instructor,
                start_time=start_time,
                end_time=end_time,
                link=generate_lecture_link()
            )
            scheduled_lectures.append(scheduled)

        last_three_lectures = scheduled_lectures[-3:]

        first_two_rescheduled_start_times = [
            last_three_lectures[1].start_time,
            last_three_lectures[2].start_time,
        ]

        response = self.lecture_controller.reschedule_lecture(
            RescheduleLectureReqDto(
                scheduled_lecture_id=last_three_lectures[0].pk
            )
        )

        rescheduled_lectures = response.scheduled_lectures

        self.assertEqual(len(rescheduled_lectures), 3)

        assert rescheduled_lectures[0].start_time == first_two_rescheduled_start_times[0]
        assert rescheduled_lectures[1].start_time == first_two_rescheduled_start_times[1]

        assert response.response_status == ResponseStatus.SUCCESS

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



