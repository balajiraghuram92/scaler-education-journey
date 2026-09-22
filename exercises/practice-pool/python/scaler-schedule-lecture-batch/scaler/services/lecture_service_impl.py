from .lecture_service import LectureService
from typing import List
from scaler.models import ScheduledLecture, Lecture, Instructor, Batch
from scaler.exceptions import InvalidInstructorError, InvalidBatchError, InvalidLectureError
from scaler.utils import get_future_schedule_dates, generate_lecture_link


class LectureServiceImpl(LectureService):

    def schedule_lectures(
            self,
            batch_id: int,
            instructor_id: int,
            lecture_ids: List[int]
    ) -> List[ScheduledLecture]:

        instructor = Instructor.objects.filter(pk=instructor_id).first()
        if not instructor:
            raise InvalidInstructorError("Instructor not found with id: " + str(instructor_id))

        batch = Batch.objects.filter(pk=batch_id).first()
        if not batch:
            raise InvalidBatchError("Batch not found with id: " + str(batch_id))

        lectures = Lecture.objects.filter(pk__in=lecture_ids)
        if len(lectures) != len(lecture_ids):
            raise InvalidLectureError("One or more lectures not found with given ids")

        last_scheduled_lecture = ScheduledLecture.objects.filter(batch=batch).order_by('-end_time').first()

        if not last_scheduled_lecture:
            raise InvalidBatchError("No existing scheduled lecture found for batch with id: " + str(batch_id))

        future_schedule_dates = get_future_schedule_dates(
            last_scheduled_lecture.end_time,
            batch.schedule,
            len(lecture_ids)
        )

        scheduled_lectures = []

        for lecture, (start_time, end_time) in zip(lectures, future_schedule_dates):
            scheduled_lecture = ScheduledLecture(
                lecture=lecture,
                batch=batch,
                instructor=instructor,
                start_time=start_time,
                end_time=end_time,
                link=generate_lecture_link()
            )
            scheduled_lecture.save()
            scheduled_lectures.append(scheduled_lecture)

        return scheduled_lectures

