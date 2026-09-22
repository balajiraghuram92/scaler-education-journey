from typing import List

from scaler.models import LearnerProgress
from scaler.services import LectureService
from scaler.dtos import AccessLectureReqDto, AccessLectureResDto
from scaler.dtos import ResponseStatus


class LectureController:
    lecture_service: LectureService

    def __init__(
            self,
            lecture_service: LectureService
    ):
        self.lecture_service = lecture_service

    def access_lecture(
            self,
            request_dto: AccessLectureReqDto
    ):

        try:
            response: LearnerProgress = self.lecture_service.access_lecture(
                learner_id=request_dto.learner_id,
                scheduled_lecture_id=request_dto.scheduled_lecture_id,
                lecture_link=request_dto.lecture_link
            )

            response_dto = AccessLectureResDto(
                learner_progress=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = AccessLectureResDto(
                learner_progress=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto


