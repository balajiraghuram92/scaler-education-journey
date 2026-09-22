from food_delivery.dtos import MatchPartnerTaskRequestDto, MatchPartnerTaskResponseDto
from food_delivery.dtos import ResponseStatus
from logging import getLogger, DEBUG
import traceback

from food_delivery.services import TaskService


class TaskController:
    task_service: TaskService

    def __init__(
            self,
            task_service: TaskService
    ):
        self.task_service = task_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def match_partners_and_tasks(
            self,
            request_dto: MatchPartnerTaskRequestDto
    ):
        try:
            mappings = self.task_service.match_partners_and_tasks(
                partner_ids=request_dto.partner_ids,
                task_ids=request_dto.task_ids
            )

            response = MatchPartnerTaskResponseDto(
                response_status=ResponseStatus.SUCCESS,
                partner_task_mappings=mappings
            )

        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = MatchPartnerTaskResponseDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
