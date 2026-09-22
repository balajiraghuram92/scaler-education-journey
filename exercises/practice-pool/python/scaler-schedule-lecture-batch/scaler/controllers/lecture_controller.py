from typing import List

from scaler.models import ScheduledLecture
from scaler.services import LectureService
from scaler.dtos import ScheduleLectureReqDto, ScheduleLectureResDto
from scaler.dtos import ResponseStatus


class LectureController:
    lecture_service: LectureService

    def __init__(
            self,
            lecture_service: LectureService
    ):
        self.lecture_service = lecture_service

    def schedule_lectures(
            self,
            request_dto: ScheduleLectureReqDto
    ):

        try:
            response: List[ScheduledLecture]= self.lecture_service.schedule_lectures(
                batch_id=request_dto.batch_id,
                instructor_id=request_dto.instructor_id,
                lecture_ids=request_dto.lecture_ids
            )

            response_dto = ScheduleLectureResDto(
                scheduled_lectures=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = ScheduleLectureResDto(
                scheduled_lectures=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto


