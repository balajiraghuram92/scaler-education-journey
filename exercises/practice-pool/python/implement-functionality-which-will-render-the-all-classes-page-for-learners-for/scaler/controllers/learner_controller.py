from typing import List

from scaler.models import ScheduledLecture
from scaler.services import LearnerService
from scaler.dtos import FetchTimelineReqDto, FetchTimelineResDto
from scaler.dtos import ResponseStatus


class LearnerController:
    learner_service: LearnerService

    def __init__(
            self,
            learner_service: LearnerService
    ):
        self.learner_service = learner_service

    def fetch_timeline(
            self,
            request_dto: FetchTimelineReqDto
    ):

        try:
            response: List[ScheduledLecture] = self.learner_service.fetch_timeline(
                learner_id=request_dto.learner_id,
            )

            response_dto = FetchTimelineResDto(
                scheduled_lectures=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = FetchTimelineResDto(
                scheduled_lectures=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto


