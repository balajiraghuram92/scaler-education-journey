from typing import List

from scaler.models import ScheduledLecture
from scaler.services import LectureService
from scaler.dtos import RescheduleLectureReqDto, RescheduleLectureResDto
from scaler.dtos import ResponseStatus


class LectureController:
    lecture_service: LectureService

    def __init__(
            self,
            lecture_service: LectureService
    ):
        self.lecture_service = lecture_service

    def reschedule_lecture(
            self,
            request_dto: RescheduleLectureReqDto
    ):

        try:
            response: List[ScheduledLecture]= self.lecture_service.reschedule_lecture(
                scheduled_lecture_id=request_dto.scheduled_lecture_id
            )

            response_dto = RescheduleLectureResDto(
                scheduled_lectures=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = RescheduleLectureResDto(
                scheduled_lectures=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto


